import datetime
import paho.mqtt.client as mqtt
import picamera
import io
import subprocess


class Cam:

    def __init__(self, pir_id, mqtt_host, mqtt_topic, local_tmp_dir, gdrive_cmd):
        # self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        # self.config.read('config.ini')
        # self.pir_id = self.config['device']['pir_id']
        # self.mqtt_host = self.config['mqtt']['mqtt_host']
        # self.mqtt_topic = self.config['mqtt']['mqtt_topic']
        # self.local_tmp_dir = self.config['gdrive']['local_tmp_dir']
        self.pir_id = pir_id
        self.mqtt_host = mqtt_host
        self.mqtt_topic = mqtt_topic
        self.local_tmp_dir = local_tmp_dir
        self.gdriveCMD = gdrive_cmd


        self.file_path_photo = '%s/photo_%s_%s.jpg'
        self.file_path_video = '%s/video_%s_%s.h264'
        self.previous_state = False
        self.current_state = False
        self.previous_datetime = datetime.datetime.now()
        self.current_datetime = datetime.datetime.now()
        self.diagnosticCounter = 0

        self.presence_detected = False

        self.mqtt_client = mqtt.Client()
        # Assign event callbacks
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        print("Program started at %s" % datetime.datetime.now())
        print("-----------------------------------------------")
        print("pir ID    : %s" % self.pir_id)
        print("mqtt host : %s" % self.mqtt_host)
        print("mqtt topic: %s" % self.mqtt_topic)
        print("photo file: %s" % self.file_path_photo)
        print("video file: %s" % self.file_path_video)
        print("-----------------------------------------------")

    def on_connect(self, client, userdata, flags, rc):
        print("on connect: " + str(rc))
        self.mqtt_client.subscribe(self.mqtt_topic, 0)

    def on_message(self, client, userdata, msg):
        print("on message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
        message = str(msg.payload)
        if "Presenza rilevata" in message:
            self.presence_detected = True
        else:
            self.presence_detected = False

    def write_photo(self, camera, timestamp):
        filename = self.file_path_photo % (self.local_tmp_dir, self.pir_id, timestamp)
        print('Writing photo %s ...' % filename)
        camera.capture(filename, resize=(1280, 768), use_video_port=True)
        print('Writing photo %s done.' % filename)
        print('Uploading photo %s ...' % filename)
        cmd = self.gdriveCMD.format(filename, filename)
        subprocess.call(cmd, shell=True)
        print('Uploading photo %s started' % filename)

    def write_video(self, video_stream, timestamp):
        filename = self.file_path_video % (self.local_tmp_dir, self.pir_id, timestamp)
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
        cmd = self.gdriveCMD.format(filename, filename)
        subprocess.call(cmd, shell=True)
        print('Uploading video %s started' % filename)

    def start(self):
        print("Connect to MQTT ...")
        self.mqtt_client.connect(self.mqtt_host, 1883, 20)
        self.mqtt_client.loop_start()
        print("Connect to MQTT done")

        with picamera.PiCamera() as self.camera:
            stream = picamera.PiCameraCircularIO(self.camera, seconds=5)
            # Turn the camera's LED off
            self.camera.led = False
            self.camera.resolution = (640, 480)
            # camera.iso = 800
            # camera.framerate = 10
            self.camera.hflip = True
            self.camera.vflip = True
            # camera.start_recording(stream, format='h264', quality=20)
            self.camera.start_recording(stream, format='h264')

            try:
                while True:
                    self.camera.wait_recording(0.1)
                    ts = datetime.datetime.now()
                    ts_str = ts.strftime('%Y-%m-%d_%H-%M-%S')
                    # ON PRESENCE
                    if self.presence_detected:
                        msg = "Presenza rilevata - %s" % ts_str
                        print(msg)
                        self.write_photo(self.camera, ts_str)
                        # Keep recording for 10 seconds and only then write the
                        # stream to disk
                        self.camera.wait_recording(10)
                        print("%s Registrazione completata per il video" % ts_str)
                        self.write_video(stream, ts_str)

            finally:
                self.camera.stop_recording()
                self.mqtt_client.loop_stop()
                print("Program ended at %s" % datetime.datetime.now())
