from PIL import Image
import sys
import numpy as np
import os 

def get_animation_as_string(filedir):
	'''convert a bitmat representing a LED animation into a string each '0' and '1' represents an on/off LED in a given frame and position'''
	im = Image.open(filedir).convert('L') # read image in BW
	mat = np.asarray(im)

	# loop over patterns
	nPats = mat.shape[0]//3 # devide number of rows by 3
	print("nPats = %d"%nPats)

	outArray = np.zeros(nPats*27, dtype='bool')

	for p in range(nPats):
		for l in range(3): # loop over the 3 levels
			outArray[p*27+l*9:p*27+(l+1)*9] = 220>mat[p*3:(p+1)*3, l*3:(l+1)*3].flatten()


	# convert numpy array to string
	outString = "".join(['%d'%i for i in np.array(outArray, dtype='uint8')])
	return outString


def string_to_binary(s, debug=False):
	''' converts string of 0 and 1 to a special bytearray'''

	N = len(s)
	n_frames = N//27
	padding = '0'*(4*8-27) # we need padding to fill out 4 bits
	bytesOut = bytearray()
	
	for i in range(n_frames): # loop over frames in animation

		# ugly code, but hopefully understandable. We need to flip the order of the bytes because of the way arduino reades bytestrings

		# The conversion works as follows:
		# A slice of eight elements from the string s are reversed and conted to an integer using int(..., 2) where '2' indicates base two.
		# These four integers are later concatenated and transformed into a binary string
		
		b1 = int(s[i*27:i*27+8][::-1], 2)
		b2 = int(s[i*27+8:i*27+16][::-1], 2)
		b3 = int(s[i*27+16:i*27+24][::-1], 2)
		b4 = int((s[i*27+24:i*27+27]+padding)[::-1], 2)

		if debug: print([b1,b2,b3,b4])

		bytesOut.extend(bytes([b1,b2,b3,b4]))

	return bytesOut

if __name__ == "__main__":
	s = get_animation_as_string(filedir = sys.argv[1])
