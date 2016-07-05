#!/usr/bin/python
"""
T Macrina
160321

Crop all TIFs in a directory and save as renamed TIFs in the directory

Args:
	sys.argv[1]: full path to the TIF image directory
	sys.argv[2:6]: x slice start, x slice end, y slice start, y slice end

Returns:
	Renamed cropped TIFs
"""

from PIL import Image
import numpy as np
import h5py
import os
import sys

def tif_to_array(fn):
	"""Open TIF image and convert to numpy ndarray of dtype

	Currently tested for only for uint8 -> uint8, uint32 or uint24 -> uint32

	Args:
		fn: filename (full path) of the image

	Returns:
		An ndarray of dtype
	"""
	img = np.array(Image.open(fn))
	if len(img.shape) == 3:
		img = np.dstack((np.zeros(img.shape[:2]+(1,)), img))
		img = img[:,:, ::-1]
		img = img.astype(np.uint8).view(np.uint32)
		img = img.reshape(img.shape[:2])
	return img

def crop_array(arr, crop):
	return arr[crop]

def crop_dir(dir, crop):
	"""Combine all TIF images in directory (sorted) into 3D ndarray

	Args:
		dir: folder path

	Returns:
		An ndarray of dtype with at least 3 dimesnions
	"""
	array = None
	files = os.listdir(dir)
	files.sort()
	for file in files:
		if file.endswith(".tif") or file.endswith(".tiff"):
			a = tif_to_array(os.path.join(dir, file))
			a = crop_array(a, crop)
			write_to_tif(fn, a)

def write_to_tif(fn, arr):
	"""Write ndarray to tif file
	"""
	img = Image.fromarray(arr)
	img.save(fn)

def main():
	"""Make HDF5 3D matrix of TIF images in a sorted directory & cropped
	"""
	dir = os.getcwd()
	if len(sys.argv) > 1:
		dir = sys.argv[1]
	crop = slice(None), slice(None), slice(None)
	if len(sys.argv) > 6:
		crop = (slice(int(sys.argv[3]), int(sys.argv[4])),
					slice(int(sys.argv[5]), int(sys.argv[6])),
					slice(None))
	array = make_array_from_tif_dir(dir)
	array = array[crop]
	array = array.transpose((2,1,0))
	fn = os.path.split(os.getcwd())[-1] + ".h5"
	if len(sys.argv) > 2:
		fn = sys.argv[2]
	if not fn.endswith(".h5"):
		fn += ".h5"
	write_to_h5(os.path.join(dir, fn), array)

if __name__ == '__main__':
	main()