'''script for controlling a LED cube and feeding it with new patterns'''
import serial
import patterngenerator
import time

class CUBE:

	def __init__(self):
		print('Created instance of LED cube')
		try:
			self.open_serial()
			print('Serial connection made. Testing connection...')
			self.send('G')
			self.send('G')
			if self.read() == 'G':
				print('Arduino responded correctly')
			else:
				print('Arduino did not respond correctly')

		except s:
			raise(s)

	def open_serial(self, port='COM3', baud=9600, timeout=0.2):
		self.s = serial.Serial(port, baud, timeout=timeout)

	def close_serial(self):
		self.s.close()

	def send(self, c):
		self.s.write(str.encode(c))

	def read(self):
		return self.s.read()

	def readline(self):
		return self.s.readline()

	def send_pat_binary(self, filedir):
		# generate binary from animation file
		s = patterngenerator.get_pattern_as_string(filedir)
		n_frames = len(s)//27
		s_binary = patterngenerator.stringToBinary(s)

		# ensure the animation is turned off, so the Arduino always listens to the serial port
		self.send('S')
		while True:
			time.sleep(0.05)
			if self.read() == b'S':
				break

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


	def send_pat(self, filedir):
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
		self.send('D'+str(x))
		time.sleep(0.1)
		print(self.readline())

	def set_frametime(self, x):
		self.send('T'+str(x))
		time.sleep(0.1)
		print(self.readline())

	def debug(self):
		# get dubug information from arduino
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
	cube = CUBE()