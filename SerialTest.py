import serial
from time import sleep
ser = serial.Serial('COM3', 9600, timeout=1)
print(ser.name)
sleep(0.1)


ser.write(b'G')
sleep(0.1)
msg = ser.read()
print('Arduino replied: %s'%msg)
