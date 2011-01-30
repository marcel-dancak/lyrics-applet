import os
import re
from operator import attrgetter

class LyricEntity:
	seconds        = None
	text           = None
	translation    = None
	height         = None
	trimmed_height = None 
	lengths        = None
	tlengths       = None
	show_time      = False # TODO implement
	
	def __init__(self, text, seconds):
		self.text = text
		self.seconds = seconds
		self.tlengths = [0]


def isCJK(text):
	#print text
	# isn't unicode ?, will be
	if not isinstance(text, unicode):
		text = unicode(text)
	
	for c in text:
		#if ord(c) > 120: print ord(c)
		if ord(c)>10000:
			return True
	return False

def parseLine(line):
	p = re.compile("^(\s)*\[(?P<min>\d(\d)?):(?P<sec>\d(\d)?(.(\d)+)?)\](?P<text>(.)*)$")
	m = p.match(line)
	if m:
		minutes = int(m.group('min'))
		seconds = float(m.group('sec'))
	
		time = minutes*60 + seconds
		text = m.group('text')
		return [time, text]
		

def parseLyrics(lyrics, filter_cjk=True):
	lines = lyrics.rsplit(os.linesep)
	processedLyrics = []
	old = -1
	for line in lines:
		#print "line: %s" % line
		times = []
		text = None
		tt = parseLine(line)
		while tt != None:
			times.append(tt[0])
			text = tt[1]
			tt = parseLine(text)
		
		#print times
		#print text
		
		if len(times) > 1:
			if not filter_cjk or not isCJK(text):
				log.debug("processing multiple timing tags")
				for t in times:
					processedLyrics.append(LyricEntity([text], t))
				
		if len(times) == 1:
			time = times[0]		
			if text == None:# or len(text) == 0:
				continue

			#print time
			#print text
			# texts with the same time or with [00:00.00] join together
			if old == time or time == 0:
				# if enabled, filter korean, chinese, japanese ...
				if filter_cjk and isCJK(text):
					continue
				if len(processedLyrics) > 0:
					processedLyrics[-1].text.append(text)
				else:
					# create new lyrics entity, if doesn't exists
					#processedLyrics.append(LyricEntity(["%s %s" % (time, text)], time)) # for debug
					processedLyrics.append(LyricEntity([text], time))
				continue
			# if enabled, filter korean, chinese, japanese ...
			if not filter_cjk or not isCJK(text):
				# create new lyrics entity
				#processedLyrics.append(LyricEntity(["%s %s" % (time, text)], time)) # for debug
				processedLyrics.append(LyricEntity([text], time))
			old = time
		
		continue	

		# parse additional info
		"""
		else:
			if not artist and line.startswith('artist:'):
				artist = line[7:]
			if not title and line.startswith('title:'):
				title = line[6:]
			if not album and line.startswith('album:'):
				album = line[6:]
		"""	
	if len(processedLyrics) == 0:
		# UNSYNCHRONIZED LYRICS
		return [lyrics]

	"""
	#insert same info about song at start, if there is "place"
	if len(processedLyrics) > 0 and processedLyrics[0].seconds > 0:
		info = []
		if self.songInfo.has_key('artist'): info.append(self.songInfo['artist'])
		if self.songInfo.has_key('album'):  info.append(self.songInfo['album'])
		if self.songInfo.has_key('title'):  info.append(self.songInfo['title'])
		info.append('')
		processedLyrics.insert(0, LyricEntity(info, 0))
	"""
	# sort it
	processedLyrics.sort(key=attrgetter('seconds'))
	return processedLyrics
