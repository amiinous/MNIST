#!/usr/bin/python3

import socket
from  http.server import BaseHTTPRequestHandler, HTTPServer
import time
import json

# FPGA imports

import sys
import math
import numpy as np
import os
import time
from PIL import Image
from matplotlib import pyplot
import cv2
from datetime import datetime
from pynq import Xlnk
from pynq import Overlay
from pynq.mmio import MMIO
from loader import loader
import scipy.misc
from IPython.display import display

print('FPGA Initializing...')
OVERLAY_PATH = 'overlay.bit'
overlay = Overlay(OVERLAY_PATH)
dma = overlay.axi_dma_0

xlnk = Xlnk()
nn_ctrl = MMIO(0x43c00000, length=1024)
print('Got nn_ctrl!')

## FPGA Parameters

height = 28
width = 28
pixel_bits = 8
pixels_per_line = 448/pixel_bits
num_lines = int((height*width)/pixels_per_line)



# hostName = "localhost"
hostName = "192.168.1.177"
hostPort = 8181

class MyServer(BaseHTTPRequestHandler):

	def _set_headers(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()
	
	def _html(self, body):
		"""This just generates an HTML document that includes `message`
		in the body. Override, or re-write this do do more interesting stuff.
		"""
		content = "<html><body>%s</body></html>" % body
		return content.encode("utf8")  # NOTE: must return a bytes object!


	def do_GET(self):
		self._set_headers()
		self.wfile.write(self._html("<p>You accessed path: " + self.path  + "</p>"))

	def do_POST(self):

		print( "incomming http: ", self.path )

		content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
		post_data = self.rfile.read(content_length) # <--- Gets the data itself
		post_data = json.loads(post_data)
		print("this is the object in post data:")

# 		print(post_data['digits'])
            
		l = loader()
		l.load_libsvm_data_array(post_data['digits'], num_features=784, one_hot=0, classes=None)
		MINIBATCH_SIZE = len(post_data['digits'])
		images = np.zeros((MINIBATCH_SIZE,28,28))
		for i in range(0, MINIBATCH_SIZE):
			images[i,:,:] = (l.a[i].reshape((28,28))).astype('int')
		in_buffer = xlnk.cma_array(shape=(MINIBATCH_SIZE*num_lines, 64), dtype=np.uint8)
		out_buffer = xlnk.cma_array(shape=(MINIBATCH_SIZE, 16), dtype=np.int32)
		print('allocated buffers')

		for i in range(0,MINIBATCH_SIZE):
			in_buffer[i*num_lines:(i+1)*num_lines, 0:56] = np.reshape(images[i,:,:], (num_lines, 56))

		start = time.time()
		nn_ctrl.write(0x0, 0) # Reset
		nn_ctrl.write(0x10, MINIBATCH_SIZE)
		nn_ctrl.write(0x0, 1) # Deassert reset
		dma.recvchannel.transfer(out_buffer)
		dma.sendchannel.transfer(in_buffer)
		end = time.time()

		time_per_image = (end-start)/MINIBATCH_SIZE
		print("Time per image: " + str(time_per_image) + " s")
		print("Images per second: " + str(1.0/time_per_image))

		time.sleep(1)
		outp = ""     
		for i in range(0,MINIBATCH_SIZE):
			print(str(np.argmax(out_buffer[i,:])))
			outp = outp + str(np.argmax(out_buffer[i,:]))
		print(outp)
		self._set_headers()
		self.wfile.write(outp.encode("utf-8"))



myServer = HTTPServer(("", hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
	myServer.serve_forever()
except KeyboardInterrupt:
	pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))