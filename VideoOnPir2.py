import RPi.GPIO as GPIO
import datetime
import paho.mqtt.publish as publish
import picamera
import io
import subprocess
import sys

sensor = 4

gdriveCMD = "/home/pi/AcchiappaLadro/gdrive/gdrive -c /home/pi/AcchiappaLadro/gdrive/conf upload -p 0B5VaZPNYmmfca0dnMDdFLXppNTA -f {} && rm {} &"

mqtt_host = "iot.eclipse.org"
mqtt_topic = "/baleani/laspio/pir/1"
file_path_photo = '/home/pi/AcchiappaLadro/photo_%s.jpg'
file_path_video = '/home/pi/AcchiappaLadro/video_%s.h264'

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

previous_state = False
current_state = False

previous_datetime = datetime.datetime.now()
current_datetime = datetime.datetime.now()

diagnosticCounter = 0

def write_photo(camera, timestamp):
    filename = file_path_photo % timestamp
    print('Writing photo %s ...' % filename)
    camera.capture(filename, resize=(1280, 768), use_video_port=True)
    print('Writing photo %s done.' % filename)

    print('Uploading photo %s ...' % filename)
    cmd = gdriveCMD.format(filename, filename)
    subprocess.call(cmd, shell=True)
    print('Uploading photo %s started' % filename)

def write_video(stream, timestamp):
    filename = file_path_video % timestamp
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
    cmd = gdriveCMD.format(filename, filename)
    subprocess.call(cmd, shell=True)
    print('Uploading video %s started' % filename)

def mqtt_publish(topic, msg, retn):
    try:
        publish.single(topic, msg, hostname=mqtt_host, retain=True)
    except:
        print("Error with publish on mqtt: ", sys.exc_info()[0])

with picamera.PiCamera() as camera:
    stream = picamera.PiCameraCircularIO(camera, seconds=5)

    # Turn the camera's LED off
    camera.led = False

    camera.resolution = (640, 480)
    # camera.iso = 800
    # camera.framerate = 10
    camera.hflip = True
    camera.vflip = True
    # camera.start_recording(stream, format='h264', quality=20)
    camera.start_recording(stream, format='h264')
    print("Program started at %s" % datetime.datetime.now())
    try:
        while True:
            # time.sleep(0.1)
            # camera.wait_recording(1)
            camera.wait_recording(0.1)
            ts_str = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

            diagnosticCounter = diagnosticCounter + 1
            if diagnosticCounter % (10*60) == 0:
                msg = "Nessuna presenza - %s " % ts_str
                print(msg)
                mqtt_publish("/baleani/laspio/pir1", msg, False)
                diagnosticCounter = 0

            previous_state = current_state
            current_state = GPIO.input(sensor)
            if current_state != previous_state:
                new_state = "HIGH" if current_state else "LOW"

                print("%s GPIO pin %s is %s" % (ts_str, sensor, new_state))

                if new_state == "HIGH":
                    print("%s Presenza rilevata !" % ts_str)

                    current_datetime = datetime.datetime.now()
                    time_delta = current_datetime - previous_datetime
                    previous_datetime = current_datetime
                    msg = "Presenza rilevata - %s (%s tempo passato: %s)" % (ts_str, new_state, time_delta)
                    mqtt_publish("/baleani/laspio/pir1", msg, True)

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
                #         try:
                #             current_datetime = datetime.datetime.now()
                #             time_delta = current_datetime - previous_datetime
                #             previous_datetime = current_datetime
                #             msg = "Nessuno - %s (%s tempo passato: %s)" % (ts_str, new_state, time_delta)
                #             publish.single("/baleani/laspio/pir1", msg, hostname="iot.eclipse.org", retain=True)
                #         except:
                #             print "Error with publish on mqtt: ", sys.exc_info()[0]

    finally:
        camera.stop_recording()
        GPIO.cleanup()
        print("Program ended at %s" % datetime.datetime.now())


