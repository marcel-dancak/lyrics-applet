#!/usr/bin/env python

import os
import sys
import logging
import traceback
import pygtk
import gtk
import pango
import gnomeapplet
import gconf
import logging
import logging.config


from players.player import Player
from lyricsengine.engine import LyricsEngine
from lyricstimer import LyricsTimer
from lyricsparser import LyricEntity
from options import OptionsDialog
import lyricsparser

pygtk.require('2.0')

INSTALL_PATH = os.path.dirname(os.path.abspath(lyricsparser.__file__))

logging.config.fileConfig(os.path.join(INSTALL_PATH, "logging.conf"))
#logging.config.fileConfig("/home/dencer/gnome-applets/lyrics-applet/logging.conf")
logger = logging.getLogger("LyricsApplet")
logger.setLevel(logging.DEBUG)


def getSongMetadata(player):
	metadata = {
		'title': player.getTitle(),
		'artist': player.getArtist(),
		'album': player.getAlbum(),
	}
	nullValues = [k for k,v in metadata.iteritems() if v is None]
	for k in nullValues:
		metadata.pop(k)
	
	return metadata

def lyricsFile(songInfo):
	if 'album' in songInfo and 'artist' in songInfo:
		lrc_folder = "%s - %s" % (songInfo['artist'], songInfo['album'])
	# only album
	elif 'album' in songInfo:
		lrc_folder = songInfo['album']
	# only artist
	elif 'artist' in songInfo:
		lrc_folder = songInfo['artist']
	else:
		lrc_folder = "Unknown"
	
	if 'title' in songInfo:
		lrc_file = songInfo['title']
	elif 'file' in songInfo:
		lrc_file = songInfo['file']
		lastDot = lrc_file.rfind('.')
		if lastDot != -1:
			lrc_file = lrc_file[:lastDot]
	else:
		lrc_file = "Unknown"
	return {'folder' : lrc_folder, 'file' : lrc_file+".lrc"}


class Lyrics(object):

	color = gtk.gdk.Color()
	font = "Sans 10"
	applet = None
	label = None
	lyrics_directory = "/home/dencer/Lyrics"

	def __init__(self):
		self.lyrics = None
		self.lyricsTimer = None
		self.player = Player()
		self.player.registerOnPlayerConnected(self.onPlayerConnected)
		self.player.registerOnSongChange(self.onSongChanged)
		self.player.registerOnPlay(self.onPlay)
		self.player.registerOnStop(self.onStop)
		self.player.registerOnElapsedChanged(self.onSeek)
		self.lyricsEngine = LyricsEngine(self.onLyricsFound, self.onEngineFinish)
		self.lyricsEngine.setLyricsSources(['alsong', 'minilyrics', 'lrcdb', 'lyricsscreenlet'])
		
		self.label = gtk.Label("Lyrics Applet")
		self.gconf_client = gconf.client_get_default()
		self.gconf_client.add_dir("/apps/lyrics_applet", gconf.CLIENT_PRELOAD_NONE)
		self.gconf_client.notify_add('/apps/lyrics_applet/color', self.color_changed)
		self.gconf_client.notify_add('/apps/lyrics_applet/font', self.font_changed)
		
		self.color_changed(None)
		self.font_changed(None)


	def color_changed(self, client, *args):
		color = self.gconf_client.get_string("/apps/lyrics_applet/color")
		if color:
			self.color = gtk.gdk.Color(color)
			self.label.modify_fg(gtk.STATE_NORMAL, self.color)

	def font_changed(self, client, *args):
		font = self.gconf_client.get_string("/apps/lyrics_applet/font")
		if font:
			self.font = font
			font_desc = pango.FontDescription(font)
			self.label.modify_font(font_desc)

	def onPlayerConnected(self):
		print "onPlayerConnected"

	def onStop(self):
		if self.lyricsTimer:
			self.lyricsTimer.pause()

	def onPlay(self):
		if self.lyricsTimer:
			self.lyricsTimer.resume()

	def onSeek(self, elapsed):
		print "## seek to:", elapsed
		if self.lyrics:
			self.lyricsTimer.pause()
			self.lyricsTimer = LyricsTimer(self.lyrics, self.update)
			self.lyricsTimer.start(elapsed)
			self.label.set_text(self.lyrics[self.lyricsTimer.actualLine].text[0].strip())

	def onSongChanged(self, songFile):
		try:
			self.lyrics = None
			if self.lyricsTimer:
				self.lyricsTimer.pause()
				self.lyricsTimer = None
		
			print "onSongChanged"
			metadata = getSongMetadata(self.player)
			metadata['file'] = songFile
		
			self.label.set_text("")
			print metadata
		
			lyrics = self.getLyricsFromDisk(metadata)
			if lyrics is None:
				self.lyricsEngine.search(metadata)
				print "searching started"
			else:
				self.onLyricsFound(lyrics)
		except:
			traceback.print_exc()


	def onLyricsFound(self, lyrics):
		if not self.lyrics and lyrics:
			print "onLyricsFound"
			try:
				parsed = lyricsparser.parseLyrics(lyrics)
				if isinstance(parsed[0], LyricEntity):
					self.lyrics = parsed
					self.lyricsTimer = LyricsTimer(self.lyrics ,self.update)
					elapsed = self.player.getElapsed()
					#print "elapsed:", elapsed
					self.lyricsTimer.start(elapsed)
					self.label.set_text(self.lyrics[self.lyricsTimer.actualLine].text[0].strip())
					self.lyricsEngine.stop()
			except:
				traceback.print_exc()

	def update(self, lyricsLine):
		lyricLine = self.lyrics[lyricsLine].text[0].strip()
		if lyricLine:
			self.label.set_text(self.lyrics[lyricsLine].text[0].strip())

	def onEngineFinish(self):
		print "onEngineFinish"

	def getLyricsFromDisk(self, songInfo):
		logger.debug("searching lyrics on disk")
		# check for .lrc file in song file directory
		lrc_file = None
		if songInfo.has_key('file'):
			lrc_file = songInfo['file'].rstrip("mp3")+"lrc" #TODO: not only mp3 expecting
		if lrc_file == None or not os.path.exists(lrc_file):
			lrc_path = lyricsFile(songInfo)
			lrc_file = os.path.join(self.lyrics_directory, lrc_path['folder'], lrc_path['file'])
			logger.debug("lyrics should be here: %s" % lrc_file)
			
		print lrc_file
		if lrc_file != None and os.path.exists(lrc_file):
			f = open(lrc_file, 'r')
			print "lyrics from file: %s" % lrc_file
			lrc = f.read()
			f.close()
			return lrc
		print "Nothing on disk"
		return None

	def show_about(self, *args):
		print args
		pass

	def show_preferences(self, *args):
		dialog = OptionsDialog(self)
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			dialog.save_preferences()
		dialog.destroy()


def sample_factory(applet, iid):
	lyrics = Lyrics()
	logger.info("creating applet")
	logger.info("__file__: %s" % os.path.abspath(__file__))
	logger.info("lyricsparser.__file__: %s" % lyricsparser.__file__)
	try:
		menu_file = open(os.path.join(INSTALL_PATH, "menu.xml"))
		menu = menu_file.read()
		menu_file.close()
	
		verbs = [('About', lyrics.show_about), ('Preferences', lyrics.show_preferences)]
		applet.setup_menu(menu, verbs, None)
		#applet.setup_menu_from_file(None, os.path.join(base_dir, "menu.xml"), None, verbs)
	except:
		pass
	
	
	applet.set_background_widget(applet)
	#applet.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color(200, 0, 0, 0))
	applet.add(lyrics.label)
	
	#applet.add_preferences("font")
	#applet.add_preferences("color")
	lyrics.applet = applet
	
	applet.show_all()
	return gtk.TRUE


if __name__ == '__main__':
	if len(sys.argv) == 2 and sys.argv[1] == "-w":
		main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		main_window.set_title("Python Applet")
		main_window.connect("destroy", gtk.main_quit)
		app = gnomeapplet.Applet()
		sample_factory(app, None)
		app.reparent(main_window)
		main_window.show_all()
		gtk.main()
		sys.exit()
	else:
		gnomeapplet.bonobo_factory("OAFIID:LyricsApplet_Factory",
							gnomeapplet.Applet.__gtype__,
							"lyrics", "0", sample_factory)
