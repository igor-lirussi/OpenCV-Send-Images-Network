import cv2
import time
from MJpegHttpStreamer import MJpegHttpStreamer
import signal

PORT=8080

# Handle graceful shutdown with Ctrl+C
def signal_handler(sig, frame):
    print("\nShutting down gracefully...")
    streamer.stop()  # Stop the MJPEG streamer
    print("Stopped")
    capture.release()  # Release the webcam
    print("Released")
    cv2.destroyAllWindows()  # Close any OpenCV windows
    sys.exit(0)  # Exit the program


# Setup signal handler for SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, signal_handler)


import time
from datetime import datetime
import os
import rospy
import cv2
import numpy as np
#import baxter #here we are importing the baxter.py interface. (cause it's in this same folder, but in your project please clone the repo as submodule and import the interface as described in the readme)
import importlib
baxter=importlib.import_module("baxter-python3.baxter") 

PI = 3.141592
WIDTH = 960
HEIGHT = 600


print("camera settings = ", (WIDTH, HEIGHT))



rospy.init_node("testing")
rospy.sleep(2.0)
robot = baxter.BaxterRobot(rate=100, arm="left")
rospy.sleep(2.0)
robot._set_camera(camera_name="left_hand_camera", state=True, width=WIDTH, height=HEIGHT, fps=30)
data = np.array(list(robot._cam_image.data), dtype=np.uint8)

robot.set_robot_state(True)

p = robot._endpoint_state.pose.position
q = robot._endpoint_state.pose.orientation
print("Position:")
print(p)
print("Orientation:")
print(q)

# Creates server MJPEG
streamer = MJpegHttpStreamer(PORT, 1048576)  # Port, 1MB buffer
streamer.start()

while not rospy.is_shutdown():
	#get image from camera
	img = np.array(list(robot._cam_image.data), dtype=np.uint8)
	img = img.reshape(int(HEIGHT), int(WIDTH), 4)
	img = img[:, :, :3].copy()
	
	# reshape
	frame = cv2.resize(img, (640,480))
	
	# Encode frame in JPEG
	ret, jpeg = cv2.imencode('.jpg', frame)
		
	
	# Send frame JPEG to server MJPEG
	streamer.stream_jpeg(jpeg.tobytes(), len(jpeg), int(time.time() * 1000))
	
	
	#set image as data
	robot._set_display_data(cv2.resize(img, (1024,600)))


robot.set_robot_state(False)
# Stop streaming
streamer.stop()
capture.release()
