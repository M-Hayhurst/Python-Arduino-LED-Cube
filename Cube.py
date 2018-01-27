'''script for controlling a LED cube and feeding it with new patterns'''
import serial
import patterngenerator
import time
import sys

class Cube:

	def __init__(self, port='COM3'):

		self.port = port

		print('Created instance of LED cube')
		self.open_serial()
		time.sleep(0.2)
		print('Serial connection made. Testing connection...')
		self.send('G') # for some reason the first message is not read by the Arduino. Please keep this line.
		self.send('G')
		time.sleep(0.1)

		x = self.read()
		print(x)

		if self.read() == b'G':
			print('Arduino responded correctly')
		else:
			print('Arduino did not respond correctly')

	def open_serial(self, baud=9600, timeout=0.2):
		self.s = serial.Serial(self.port, baud, timeout=timeout)

	def close_serial(self):
		self.s.close()

	def send(self, c):
		self.s.write(str.encode(c))

	def read(self):
		return self.s.read()

	def readline(self):
		return self.s.readline()

	def send_ani_binary(self, filedir):
		'''Read the animation in the image specified from filedir, convert to a binary string and send to the arduino.
		'''
		s = patterngenerator.get_animation_as_string(filedir)
		n_frames = len(s)//27
		s_binary = patterngenerator.string_to_binary(s)

		# ensure the animation is turned off, so the Arduino always listens to the serial port
		self.send('S')

		for i in range(20): # use a for loop rather while to avoid an infinite wait
			time.sleep(0.05)
			if self.read() == b'S':
				break
		else:
			exception('Arduino did not respond correctly after being instructed to stop playback')

		# update number of frames
		self.send('N%d\n'%n_frames)
		time.sleep(0.1)
		print(self.readline()[::-2])

		# send the actuall pattern
		self.send('P')
		self.s.write(s_binary)
		time.sleep(0.3)
		print(self.readline()[::-2])

		# restart animation
		self.send('R')
		time.sleep(0.05)


	def send_ani(self, filedir):
		'''legacy function where the animation is sent as a string of '1' and '0's instead for a bytearray'''
		s = patterngenerator.get_pattern_as_string(filedir)
		n_frames = len(s)//27

		# update number of frames
		self.send('N%d\n'%n_frames)
		time.sleep(0.1)
		print(self.readline()[::-2])

		# send the actuall pattern
		self.send('P'+s)
		time.sleep(0.3)
		print(self.readline()[::-2])

	def set_duty(self, x):
		'''Set the LED duty cycle which influence brightness.
		Must be an integer between 1 and 100'''
		x = int(x)
		if x>0 and x<=100:
			self.send('D'+str(x))
			time.sleep(0.1)
			print(self.readline())
		else:
			exception('Invalid dutycycle (must be between 1 and 100)')

	def set_frametime(self, x):
		'''Set frame duration in ms'''
		self.send('T'+str(x))
		time.sleep(0.1)
		print(self.readline())

	def debug(self):
		'''Get debug information from Arduino.
		Print relevant system varibles'''
		self.send('H')

		# wait for Arduino to go into serial mode
		while True:
			if self.read() == b'H':
				print('H')
				break
			else:
				time.sleep(0.2)

		time.sleep(2) # I dont believe this is necessary s.readline() will only read one line from the buffer at a time.

		nLines = 0
		while True:
			msgin = self.s.readline()
			print(msgin)
			nLines += 1
			if msgin == b'END\r\n' or nLines > 20:
				break


if __name__ == '__main__':
	cube = Cube(port=sys.argv[1])