import socket
import threading
import time

# Ensure compatibility for Python 2 and 3
import sys
if sys.version_info[0] < 3:  # Python 2
    to_bytes = lambda s: s  # Strings are already bytes in Python 2
else:  # Python 3
    to_bytes = lambda s: s.encode('utf-8')  # Convert strings to bytes in Python 3


PORT=8080

BOUNDARY = "--gc0p4Jq0M2Yt08jU534c0p--"
BOUNDARY_LINES = "\r\n" + BOUNDARY + "\r\n"

HTTP_HEADER = (
    "HTTP/1.0 200 OK\r\n"
    + "Server: Peepers\r\n"
    + "Connection: close\r\n"
    + "Max-Age: 0\r\n"
    + "Expires: 0\r\n"
    + "Cache-Control: no-store, no-cache, must-revalidate, pre-check=0, "
    + "post-check=0, max-age=0\r\n"
    + "Pragma: no-cache\r\n"
    + "Access-Control-Allow-Origin:*\r\n"
    + "Content-Type: multipart/x-mixed-replace; "
    + "boundary=" + BOUNDARY + "\r\n"
    + BOUNDARY_LINES
)

class MJpegHttpStreamer:
    def __init__(self, port, buffer_size):
        self.port = port
        self.buffer_size = buffer_size
        self.buffer_a = bytearray(buffer_size)
        self.buffer_b = bytearray(buffer_size)
        self.length_a = -1
        self.length_b = -1
        self.timestamp_a = -1
        self.timestamp_b = -1
        self.streaming_buffer_a = True
        self.new_jpeg = False
        self.buffer_lock = threading.Condition()
        self.running = False
        self.worker_thread = None

    def get_local_ip(self):
        try:
            # Create a UDP socket and connect to a public server
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Google's public DNS
            ip_address = s.getsockname()[0]  # Get the local IP
            s.close()
            return ip_address
        except Exception as e:
            return "Error: Unable to determine IP address. {}".format(e)

    def start(self):
        if self.running:
            raise Exception("MJpegHttpStreamer already in execution")
        self.running = True
        self.worker_thread = threading.Thread(target=self.worker_run)
        self.worker_thread.start()
        print("Streaming started")
        print("On this device connect on: http://127.0.0.1:"+str(PORT))
        print("Or connect on the same network on: http://{}:{}".format(self.get_local_ip(), PORT))

    def stop(self):
        if not self.running:
            raise Exception("MJpegHttpStreamer already stopped")
        self.running = False
        with self.buffer_lock:
            self.buffer_lock.notify_all()  # Notify any threads that may be waiting
        if self.worker_thread:
            self.worker_thread.join()
        print("Streaming stopped")

    def stream_jpeg(self, jpeg, length, timestamp):
        with self.buffer_lock:
            if self.streaming_buffer_a:
                buffer = self.buffer_b
                self.length_b = length
                self.timestamp_b = timestamp
            else:
                buffer = self.buffer_a
                self.length_a = length
                self.timestamp_a = timestamp
            buffer[:length] = jpeg[:length]
            self.new_jpeg = True
            self.buffer_lock.notify()

    def worker_run(self):
        while self.running:
            try:
                self.accept_and_stream()
            except Exception as e:
                print("Error during streaming!!"+str(e))

    def accept_and_stream(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("", self.port))
        server_socket.listen(1)
        while self.running:
            client_socket, client_address = server_socket.accept()
            print("Connection from "+str(client_address))
            try:
                client_socket.send(HTTP_HEADER.encode()) 
                while self.running:
                    with self.buffer_lock:
                        while not self.new_jpeg and self.running:
                            self.buffer_lock.wait()  # Wait for new jpeg, or if running flag is False
                        if not self.running:
                            break  # Exit the loop if the server is shutting down
                        self.streaming_buffer_a = not self.streaming_buffer_a
                        if self.streaming_buffer_a:
                            buffer = self.buffer_a
                            length = self.length_a
                            timestamp = self.timestamp_a
                        else:
                            buffer = self.buffer_b
                            length = self.length_b
                            timestamp = self.timestamp_b
                        self.new_jpeg = False
                    headers = "Content-type: image/jpeg\r\nContent-Length: {}\r\nX-Timestamp: {}\r\n\r\n".format(length, timestamp)
                    # Send data
                    client_socket.send(to_bytes(headers))  # Convert headers to bytes if needed
                    client_socket.send(buffer[:length])  # Send the JPEG buffer
                    client_socket.send(to_bytes(BOUNDARY_LINES))  # Convert boundary lines to bytes if needed
            except Exception as e:
                print("Error during streaming"+str(e))
            finally:
                client_socket.close()
        server_socket.close()


import cv2
import time

import signal
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

#streams camera
capture = cv2.VideoCapture(0)

# Creates server MJPEG
streamer = MJpegHttpStreamer(PORT, 65536)  # Port, 64KB buffer
streamer.start()

while True:
    # Captures frame of webcam
    ret, frame = capture.read()
    # Encode frame in JPEG
    ret, jpeg = cv2.imencode('.jpg', frame)
    # Send frame JPEG to server MJPEG
    streamer.stream_jpeg(jpeg.tobytes(), len(jpeg), int(time.time() * 1000))


# Stop streaming
streamer.stop()
capture.release()