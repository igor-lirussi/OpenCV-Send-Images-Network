#reads argument passed as the argument of video capture module of cv2
import numpy as np
import cv2
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--s', help='Source to play, es: --s=http://10.1.21.223:8080', default=0)
args = parser.parse_args()

print("--"*30)
print("passed:")
print(args.s)
print("--"*30)

cap = cv2.VideoCapture(args.s)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Our operations on the frame come here
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
