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

#streams camera
capture = cv2.VideoCapture(0)

# Creates server MJPEG
streamer = MJpegHttpStreamer(PORT, 1048576)  # Port, 1MB buffer
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