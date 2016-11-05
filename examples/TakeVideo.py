import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (640, 480)
    camera.start_recording('video.h264', format='h264')
    camera.wait_recording(30)
    camera.stop_recording()