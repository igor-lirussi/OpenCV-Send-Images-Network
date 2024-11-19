# Allows multiple connections, can be seen by the browser or by raw_stream_client, but not with a normal capture
# Serve the image as HTTP in MIME multipart JPG format and each image replaces the previous
import socket 
import cv2
import threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import time
import os
capture=None
PORT=8080

class CamHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith('/exit'):
			print("os exit")
			os._exit(0)
		self.send_response(200)
		self.send_header('Content-type','multipart/x-mixed-replace; boundary=jpgboundary')
		self.end_headers()
		while True:
				try:
					# capture image from camera
					rc,img = capture.read()
					if not rc:
							continue
							
					# play with image to be displayed - example "scribbling" with line, rectangle with a circle in it, half an ellipse, and top part of some text
					# note that in Python many but not all the draw functins will also return the image
					# line(img...) is basic - img is changed; can also use img = line(img...), and another copy can be made with img2 = line(img...) (I think)
					cv2.line(img,(0,0),(511,511),(255,0,0),5)
					cv2.rectangle(img,(384,0),(510,128),(0,255,0),3)
					cv2.circle(img,(447,63), 63, (0,0,255), -1)
					cv2.ellipse(img,(256,256),(100,50),0,0,180,255,-1)
					cv2.putText(img,'OpenCV',(10,500), cv2.FONT_HERSHEY_SIMPLEX, 4,(255,255,255),2,cv2.LINE_AA)
					# done playing with image
					
					img_str = cv2.imencode('.jpg', img)[1].tobytes() # change image to jpeg format
					self.send_header('Content-type','image/jpeg')
					self.end_headers()
					self.wfile.write(img_str)
					self.wfile.write(b"\r\n--jpgboundary\r\n") # end of this part
				except KeyboardInterrupt:
					# end of the message - not sure how we ever get here, though
					print("KeyboardInterrpt in server loop - breaking the loop (server now hung?)")
					self.wfile.write(b"\r\n--jpgboundary--\r\n")
					break
				except ConnectionResetError:
					print("ConnectionResetError")
					break
				except BrokenPipeError:
					print("BrokenPipeError")
					break
				except ConnectionAbortedError:
					print("ConnectionAbortedError")
					break
		return
            
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	IPAddr=s.getsockname()[0]
	print("Computer IP Address is: "+IPAddr)
	print("Connect on: http://{}:{}".format(IPAddr, PORT))


	global capture
	capture = cv2.VideoCapture(0) # connect openCV to camera 0
	
	# set desired camera properties
	capture.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) # 0.25 is turn OFF auto exposure (Logitech); 0.75 is ON
	time.sleep(.5) # wait for auto exposure change to be set
	capture.set(cv2.CAP_PROP_EXPOSURE, .01) # fairly dark - low exposure

	# a few other properties that can be set - not a complete list
	#	capture.set(cv2.CAP_PROP_BRIGHTNESS, .4); #1 is bright 0 or-1 is dark .4 is fairly dark default Brightness  0.5019607843137255
	#	capture.set(cv2.CAP_PROP_CONTRAST, 1); 
	#	capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320); 
	#	capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240);
	#	capture.set(cv2.CAP_PROP_SATURATION,0.2);

	try:
		server = ThreadedHTTPServer(('', PORT), CamHandler)
		print("server started. Call http://{}:{}/exit to QUIT".format(IPAddr, PORT))
		server.serve_forever()
		
	except KeyboardInterrupt:
		# ctrl-c comes here but need another to end all.  Probably should have terminated thread here, too.
		print("KeyboardInterrpt in server - ending server")
		capture.release()
		server.socket.close()

if __name__ == '__main__':
	main()