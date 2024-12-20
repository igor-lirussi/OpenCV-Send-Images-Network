# OpenCV-Send-Images-Network
Send and receive images / stream video through network with low latency for external computation.

Image/Video streamed can be seen with browser in another device, or captured with OpenCV for further computation. 

Technology used is Motion JPEG over HTTP. 

The server does _not require extra packages_ installation (like Flask) and it's _Python 2 compatible_ because has been used on a robot not updatable.

### Advantages:
- no extra packages needed
- python 2/3 compatible
- image stream can be captured directly with OpenCV cap.read() method.
- low latency, good for real-time

### Used:
- Python 2 / 3
- OpenCV 3.4.5

### Files: 
- MJpegHttpStreamer: pure server that streams video/images (i.e. from webcam), only 1 client.
- OpenCV_MJPEG_Streaming_Server: Server example that streams the webcam.
- OpenCV_read_source_from_argument_client: Client example that reads the images/video streamed on another device.
- raw_stream_client_read_opencv: Server that can handle multiple clients, but the format can't be captured with OpenCV cap.read() method, but with the client below.
- raw_stream_server: Client for the server above, can decode the stream.
- robot_baxter_stream_pic: an example of mine for a Baxter Robot

> If any problem or unstable connection, try shaping your frames in (480,640,3) datatype: uint8, before encoding them in .jpg .

### Other useful resources:

https://github.com/switchdoclabs/SDL_Pi_MJPEGStream

https://github.com/janakj/py-mjpeg

https://gist.github.com/n3wtron/4624820

https://github.com/foxdog-studios/peepers/tree/master
	