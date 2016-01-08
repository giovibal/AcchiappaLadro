import RPi.GPIO as GPIO
import time
import datetime
import paho.mqtt.publish as publish
import picamera
import io
import subprocess

sensor = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

previous_state = False
current_state = False

def write_photo(camera, timestamp):
    filename = 'photo_%s.jpg' % timestamp
    print('Writing photo %s ...' % filename)
    camera.capture(filename, resize=(320, 240))
    print('Writing photo %s done.' % filename)

    print('Uploading photo %s ...' % filename)
    cmd = "./gdrive/gdrive -c ./gdrive/conf upload -p 0B5VaZPNYmmfca0dnMDdFLXppNTA -f ./{} && rm ./{} &".format(filename, filename)
    subprocess.call(cmd, shell=True)
    print('Uploading photo %s started' % filename)

def write_video(stream, timestamp):
    filename = 'motion_%s.h264' % timestamp
    print('Writing video %s ...' % filename)
    with stream.lock:
        # Find the first header frame in the video
        for frame in stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                stream.seek(frame.position)
                break
        # Write the rest of the stream to disk
        with io.open(filename, 'wb') as output:
            output.write(stream.read())

    print('Writing video %s done.' % filename)

    print('Uploading video %s ...' % filename)
    cmd = "./gdrive/gdrive -c ./gdrive/conf upload -p 0B5VaZPNYmmfca0dnMDdFLXppNTA -f ./{} && rm ./{} &".format(filename, filename)
    subprocess.call(cmd, shell=True)
    print('Uploading video %s started' % filename)

with picamera.PiCamera() as camera:
    stream = picamera.PiCameraCircularIO(camera, seconds=1)
    # camera.resolution = (640, 480)
    camera.framerate = 10
    camera.hflip = True
    camera.vflip = True
    camera.start_recording(stream, format='h264', quality=20)
    try:
        while True:
            # time.sleep(0.1)
            camera.wait_recording(1)
            previous_state = current_state
            current_state = GPIO.input(sensor)
            if current_state != previous_state:
                new_state = "HIGH" if current_state else "LOW"

                ts_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                print("%s GPIO pin %s is %s" % (ts_str, sensor, new_state))

                if new_state == "HIGH":
                    print("%s Presenza rilevata !" % ts_str)

                    # infrared lamp on
                    # turn_light_on()

                    write_photo(camera, ts_str)

                    # Keep recording for 10 seconds and only then write the
                    # stream to disk
                    camera.wait_recording(10)
                    print("%s Registrazione completata per il video" % ts_str)
                    write_video(stream, ts_str)

                # else:
                #     if new_state == "LOW":
                #         print("%s Registrazione completata per il video" % ts_str)
                #         write_video(stream, ts_str)


    finally:
        camera.stop_recording()
        GPIO.cleanup()

print("Closing pirtest2 session ...")

