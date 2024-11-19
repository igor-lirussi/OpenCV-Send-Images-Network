# reads the stream from raw_stream_server and process it with OpenCV
import cv2
import urllib.request
import numpy as np
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--s', help='Source to play, es: --s=http://79.123.176.58:8080', default="http://79.123.176.58:8080")
args = parser.parse_args()

print("--"*30)
print("passed:")
print(args.s)
print("--"*30)


#if len(sys.argv)>1:
#    host = sys.argv[1]

hoststr = args.s

stream=urllib.request.urlopen(hoststr)

bytes=b''
while True:
    bytes+=stream.read(1024)
    a = bytes.find(b'\xff\xd8')
    b = bytes.find(b'\xff\xd9')
    if a!=-1 and b!=-1:
        jpg = bytes[a:b+2]
        bytes= bytes[b+2:]
        i = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
        cv2.imshow(hoststr,i)
        if cv2.waitKey(1) ==27:
            exit(0)