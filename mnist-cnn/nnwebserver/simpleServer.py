#!/usr/bin/python3

import socket
from  BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import time
import json

# hostName = "localhost"
hostName = "192.168.0.100"
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
		for key in post_data:
			print(" ", key, ":", post_data[key])
		self._set_headers()
		self.send_response(200)
		self.wfile.write(self._html("some data")) # send an HTML as response


myServer = SocketServer.TCPServer(("", hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
	myServer.serve_forever()
except KeyboardInterrupt:
	pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
