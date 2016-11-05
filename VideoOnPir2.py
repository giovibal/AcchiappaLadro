import RPi.GPIO as GPIO
import datetime
import paho.mqtt.publish as publish
import picamera
import io
import subprocess
import sys
import json
import configparser

# pir_id = "1"
# mqtt_host = "iot.eclipse.org"
# mqtt_topic = "/baleani/laspio/pir/%s" % pir_id
file_path_photo = '/home/pi/AcchiappaLadro/photo_%s_%s.jpg'
file_path_video = '/home/pi/AcchiappaLadro/video_%s_%s.h264'

# gdriveCMD = "/home/pi/AcchiappaLadro/gdrive/gdrive -c /home/pi/AcchiappaLadro/gdrive/conf upload -p 0B5VaZPNYmmfca0dnMDdFLXppNTA -f {} && rm {} &"

sensor = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

previous_state = False
current_state = False

previous_datetime = datetime.datetime.now()
current_datetime = datetime.datetime.now()

diagnosticCounter = 0


def configure():
    config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
    config.read('config.ini')
    return config


def write_photo(camera, timestamp):
    filename = file_path_photo % (pir_id, timestamp)
    print('Writing photo %s ...' % filename)
    camera.capture(filename, resize=(1280, 768), use_video_port=True)
    print('Writing photo %s done.' % filename)

    print('Uploading photo %s ...' % filename)
    cmd = gdriveCMD.format(filename, filename)
    subprocess.call(cmd, shell=True)
    print('Uploading photo %s started' % filename)


def write_video(video_stream, timestamp):
    filename = file_path_video % (pir_id, timestamp)
    print('Writing video %s ...' % filename)
    with video_stream.lock:
        # Find the first header frame in the video
        for frame in video_stream.frames:
            if frame.frame_type == picamera.PiVideoFrameType.sps_header:
                video_stream.seek(frame.position)
                break
        # Write the rest of the video_stream to disk
        with io.open(filename, 'wb') as output:
            output.write(video_stream.read())

    print('Writing video %s done.' % filename)

    print('Uploading video %s ...' % filename)
    cmd = gdriveCMD.format(filename, filename)
    subprocess.call(cmd, shell=True)
    print('Uploading video %s started' % filename)


def mqtt_publish(topic, msg, retn, v, ts, device_id):
    try:
        pubmsg = json.dumps({'devid':device_id,'msg': msg, 'v': v, 'ts': ts.isoformat()})
        publish.single(topic, pubmsg, hostname=mqtt_host, retain=retn)
    except:
        print("Error with publish on mqtt: ", sys.exc_info()[0])


with picamera.PiCamera() as camera:
    config = configure()
    pir_id = config['device']['pir_id']
    mqtt_host = config['mqtt']['mqtt_host']
    mqtt_topic = config['mqtt']['mqtt_topic']
    gdriveCMD = config['gdrive']['cmd']

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
    print("-----------------------------------------------")
    print("pir ID    : %s" % pir_id)
    print("mqtt host : %s" % mqtt_host)
    print("mqtt topic: %s" % mqtt_topic)
    print("photo file: %s" % file_path_photo)
    print("video file: %s" % file_path_video)
    print("-----------------------------------------------")
    try:
        while True:
            # time.sleep(0.1)
            # camera.wait_recording(1)
            camera.wait_recording(0.1)
            ts = datetime.datetime.now()
            ts_str = ts.strftime('%Y-%m-%d_%H-%M-%S')

            diagnosticCounter += 1
            if diagnosticCounter % (10*60) == 0:
                msg = "Nessuna presenza - %s " % ts_str
                print(msg)
                mqtt_publish(mqtt_topic, msg, False, 0, ts, pir_id)
                diagnosticCounter = 0

            previous_state = current_state
            current_state = GPIO.input(sensor)
            if current_state != previous_state:
                new_state = "HIGH" if current_state else "LOW"

                print("%s GPIO pin %s is %s" % (ts_str, sensor, new_state))

                if new_state == "HIGH":
                    print("%s Presenza rilevata !" % ts_str)

                    # current_datetime = datetime.datetime.now()
                    # time_delta = current_datetime - previous_datetime
                    # previous_datetime = current_datetime
                    msg = "Presenza rilevata - %s" % ts_str
                    mqtt_publish(mqtt_topic, msg, False, 1, ts, pir_id)

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
                #         try:_datetime
                #             msg = "Nessuno - %s" % ts_str
                #             publish.single("/baleani/laspio/pir1", msg, hostname="iot.eclipse.org", retain=True)
                #         except:
                #             print "Error with publish on mqtt: ", sys.exc_info()[0]

    finally:
        camera.stop_recording()
        GPIO.cleanup()
        print("Program ended at %s" % datetime.datetime.now())


