"""
pywinmm:
this python library can help you to control your audio files where it support a lot of file formats.
video files will be supported through updates
this library is using the winmulty media dll (winmm.dll) that comes with windows.
am trying to make it simple as i can
so please support with ideas or you can help on github project
https://github.com/baaziznasser/pywinmm
"""

#import libraries
from ctypes import windll, c_buffer
import random as rnd

#create a class to control mci
class _mci:
	#init the class
	def __init__(self):
		#load the dll
		self.w32mci = windll.winmm.mciSendStringA
		self.w32mcierror = windll.winmm.mciGetErrorStringA

	#function to send commands to dll
	def send(self, command):
		buffer = c_buffer(255)
		errorcode = self.w32mci(str(command).encode(), buffer, 254, 0)
		if errorcode:
			return errorcode, self.get_error(errorcode)
		else:
			return errorcode, buffer.value
	#get errors
	def get_error(self, error):
		error = int(error)
		buffer = c_buffer(255)
		self.w32mcierror(error, buffer, 254)
		return buffer.value

	#send direct messages
	def directsend(self, txt):
		(err, buf) = self.send(txt)
		if err != 0:
			print('Error %s for "%s": %s' % (str(err), txt, buf))
		return (err, buf)

#defining the player class
class player(object):
	#init the class
	def __init__(self, filename = "", rec = False):
		filename = filename.replace('/', '\\')
		self.filename = filename
		self._alias = 'player_%s' % str(rnd.random())
		self._mci = _mci()

		#open the snd hendle
		if not (rec):
			self.recorder = False
			self._mci.directsend(r'open "%s" alias %s' % (filename, self._alias ))
			self._mci.directsend('set %s time format milliseconds wait' % (self._alias))
			(err, buf) = self._mci.directsend('status %s length' % (self._alias))
			self._length_ms = int(buf)
		else:
			self._mci.directsend('open new Type waveaudio alias %s' % (self._alias ))
			self._mci.directsend('set %s time format milliseconds bitspersample 16 channels 2 samplespersec 44100 bytespersec 192000 alignment 4 wait' % (self._alias))
			self.recorder = True
		self.options = ""

#	#control looping
	def loop(self, b_loop = False):
		if b_loop:
			if "repeat" in self.options:
				return True
			if self.options == "":
				self.options = "repeat"
			else:
				self.options += " repeat"
		else:
			self.options = self.options.replace("repeat", "")
			self.options = self.options.replace("  ", " ")

		#controling the reverce
	def reverse(self, b_reverse = False):
		if b_reverse:
			if "reverse" in self.options:
				return True
			if self.options == "":
				self.options = "reverse"
			else:
				self.options += " reverse"
		else:
			self.options = self.options.replace("reverse", "")
			self.options = self.options.replace("  ", " ")

	#start recording
	#options you can find them on (https://docs.microsoft.com/en-us/windows/win32/multimedia/record)
	def record(self, options = ""):
		err,buf=self._mci.directsend('record %s %s' % (self._alias, options))
		return buf
	#save recorded stream to wav file
	#options you can find them on (https://docs.microsoft.com/en-us/windows/win32/multimedia/save)
	def save(self, file,options = ""):
		err,buf=self._mci.directsend('save %s %s %s' % (self._alias, file, options))
		return buf

	#play the opened audio file
	#options are in (https://docs.microsoft.com/en-us/windows/win32/multimedia/play)
	def play(self, options = ""):
		if options != "":
			options = " " + options
			options = options.replace("  ", " ")
		#setting position to 0 to be able to play
		self.setposition(0)
		err,buf=self._mci.directsend('play %s %s' % (self._alias, self.options + options))
		return buf

	#check if the file is playing
	def isplaying(self):
		return self.status() == 'playing'

	#get status of the loaded file or recording~
	#options are in (https://docs.microsoft.com/en-us/windows/win32/multimedia/status)
	def status(self, option = "mode"):
		err, buf = self._mci.directsend('status %s %s' % (self._alias, option))
		return str(buf)

	#pause player or recorder
	def pause(self):
		self._mci.directsend('pause %s' % self._alias)
	#resume the player or the recorder
	def resume(self):
		self._mci.directsend('resume %s' % self._alias)
	#check if file or recorder is paused
	def ispaused(self):
		return self._mode() == 'paused'

	#stop player or recorder
	def stop(self):
		self._mci.directsend('stop %s' % self._alias)
	#get the length of the player or the recorded time
	def getlength(self):
		if not (self.recorder):
			return self._length_ms
		else:
			(err, buf) = self._mci.directsend('status %s length' % (self._alias))
			return int(buf)

	#get the current position
	def getposition(self):
		(err, buf) = self._mci.directsend('status %s position' % (self._alias))
		return int(buf)

	#set the position of the player
	#you have to use the play function after using this function because some time it causes player stop
	def setposition(self, pos):
		pos = int(pos)
		if pos > self.getlength():
			pos = getlength()
		elif pos < 0:
			pos = 0
		self._mci.directsend('set %s time format milliseconds' % (self._alias))
		(err, buf) = self._mci.directsend('seek %s to %d' % (self._alias, pos))

	#set the volume
	def setvolume(self, vol):
		if vol > 100:
						vol = 100
		elif vol < 0:
			vol = 0
		self._mci.directsend('setaudio %s volume to %d' % (self._alias, vol * 10) )

	#get volume
	def getvolume(self):
		try:
			(err, buf) = self._mci.directsend('status %s volume' % (self._alias) )
			if err != 0:
				return 0
			else:
				return int(int(buf)/10)
		except:
			return 0

	#unload file
	def unload(self):
		self._mci.directsend('close %s' % self._alias)
