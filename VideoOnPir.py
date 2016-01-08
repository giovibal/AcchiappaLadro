import io
import random
import picamera
import RPi.GPIO as GPIO
import time
import datetime
import paho.mqtt.publish as publish
import subprocess

sensor = 4

relay_ch1 = 17
relay_ch2 = 18
relay_ch3 = 27
relay_ch4 = 22


GPIO.setmode(GPIO.BCM)

# pir setup
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

# relay setup
GPIO.setup(relay_ch1, GPIO.OUT)
GPIO.setup(relay_ch2, GPIO.OUT)
GPIO.setup(relay_ch3, GPIO.OUT)
GPIO.setup(relay_ch4, GPIO.OUT)

# previous_state = False
# current_state = False
# presenza_rilevata = 0

def presence_detected():
    # Randomly return True (like a fake motion detection routine)
    #return random.randint(0, 10) == 0

    # detect pir motion
    pir_state = GPIO.input(sensor)

    # previous_state = current_state
    # current_state = GPIO.input(sensor)
    # if current_state != previous_state:
    #     pir_state = "HIGH" if current_state else "LOW"

    print('Presence ==> %s' % pir_state)
    return pir_state


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


def write_photo(camera, timestamp):
    filename = 'photo_%s.jpg' % timestamp
    print('Writing photo %s ...' % filename)
    camera.capture(filename, resize=(320, 240))
    print('Writing photo %s done.' % filename)

    print('Uploading photo %s ...' % filename)
    cmd = "./gdrive/gdrive -c ./gdrive/conf upload -p 0B5VaZPNYmmfca0dnMDdFLXppNTA -f ./{} && rm ./{} &".format(filename, filename)
    subprocess.call(cmd, shell=True)
    print('Uploading photo %s started' % filename)

def turn_light_on():
    GPIO.output(relay_ch1, GPIO.HIGH)

def turn_light_off():
    GPIO.output(relay_ch1, GPIO.LOW)

with picamera.PiCamera() as camera:
    stream = picamera.PiCameraCircularIO(camera, seconds=1)
    # camera.resolution = (640, 480)
    camera.framerate = 10
    camera.hflip = True
    camera.vflip = True
    camera.start_recording(stream, format='h264', quality=20)
    try:
        while True:
            camera.wait_recording(1)

            presenza_rilevata = presence_detected()
            if presenza_rilevata == 1:
                ts_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                print("%s Presenza rilevata !" % ts_str)

                # infrared lamp on
                # turn_light_on()

                # write_photo(camera, ts_str)

                # Keep recording for 10 seconds and only then write the
                # stream to disk
                camera.wait_recording(10)
                print("%s Registrazione completata per il video" % ts_str)
                write_video(stream, ts_str)

            # else:
                # infrared lamp off
                # turn_light_off()

    finally:
        camera.stop_recording()
        GPIO.cleanup()
