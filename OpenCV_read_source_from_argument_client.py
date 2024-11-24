#reads argument passed as the argument of video capture module of cv2
import numpy as np
import cv2
import argparse

print(" This program can read and display with OpenCV video sources streamed,")
print(" by cameras on the device (0,1,2,..) or network (http://10.1.21.223:8080)")
print(" You can pass the source -s to test as an argument: --s=http://10.1.21.223:8080")
print(" Exit with q \n")

parser = argparse.ArgumentParser()
parser.add_argument('--s', help='Source to play, es: --s=http://10.1.21.223:8080', default=0)
parser.add_argument('--record','--r', action='store_true', help='Record to video file')
args = parser.parse_args()

print("--"*30)
print("passed:")
print(args.s)
print("--"*30)

cap = cv2.VideoCapture(args.s)

if args.record:
    print("Recording Enabled")
    ret, frame = cap.read()
    height, width = frame.shape[:2]
    print(frame.shape[:2])
    video_writer = cv2.VideoWriter('recording.avi', cv2.VideoWriter_fourcc(*'MJPG'), 10, (width, height)) 

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Write to file if requested
    if args.record: 
        video_writer.write(frame)

    # Display the resulting frame
    #print(frame.shape)
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done
if args.record:
	video_writer.release() 
cap.release()
cv2.destroyAllWindows()
