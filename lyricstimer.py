import gobject
import traceback

class TimeLine(object):
	elapsed = 0
	real    = 0.0
	stopped = True

	def start(self, elapsed=0):
		self.elapsed = elapsed
		self.real = gobject.get_current_time()
		self.stopped = False

	def setTime(self, time):
		print "SET TIME %f" % time
		self.elapsed = time
		self.real = gobject.get_current_time()

	def pause(self):
		if not self.stopped:
			self.elapsed += (gobject.get_current_time() - self.real)
			self.stopped = True

	def resume(self):
		if self.stopped:
			self.real = gobject.get_current_time()
			self.stopped = False

	def getTime(self):
		if self.stopped:
			return self.elapsed
		
		return self.elapsed+(gobject.get_current_time() - self.real)

class LyricsTimer(object):

	def __init__(self, lyrics, callback):
		self.lyrics = lyrics
		self.callback = callback
		self.actualLine = 0
		self.timer = None
		self.timeline = TimeLine()

	def start(self, elapsed=0):
		self.timeline.start(elapsed)
		self.synchronizeLyrics(elapsed)
		#next = self.lyrics[self.actualLine+1].seconds-elapsed
		#gobject.timeout_add(int(next*1000.0), self._update)
		self._setupTimeout(elapsed)

	def _update(self):
		print "** update **", self.timeline.stopped
		if not self.timeline.stopped:
			self.actualLine += 1
			elapsed = self.timeline.getTime()
			print "line: ", self.actualLine, "elapsed:", elapsed
			self._setupTimeout(elapsed)
			self.callback(self.actualLine)

	def _setupTimeout(self, elapsed):
		if self.actualLine+1 < len(self.lyrics):
			next = self.lyrics[self.actualLine+1].seconds-elapsed
			#print next
			self.timer = gobject.timeout_add(int(next*1000.0), self._update)
		return False

	def pause(self):
		self.timeline.pause()
		if self.timer:
			print "canceling timer"
			gobject.source_remove(self.timer)
			self.timer = None

	def resume(self):
		self.timeline.resume()
		elapsed = self.timeline.getTime()
		self._setupTimeout(elapsed)

	def setTime(self, elapsed):
		self.timeline.setTime(elapsed)
		#TODO

	def synchronizeLyrics(self, elapsed):
		for i,lyric in enumerate(self.lyrics):
			#print "%f > %f [%s]" % (lyric.seconds, elapsed, lyric.text[0])
			if lyric.seconds > elapsed:
				self.actualLine = i-1
				return
		# set last line
		self.actualLine = len(self.lyrics)-1
