import RPi.GPIO as GPIO
import datetime
import paho.mqtt.publish as publish
import sys
import json
import time

class Pir:

    def __init__(self, pir_id, mqtt_host, mqtt_topic):
        # self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        # self.config.read('config.ini')
        # self.pir_id = self.config['device']['pir_id']
        # self.mqtt_host = self.config['mqtt']['mqtt_host']
        # self.mqtt_topic = self.config['mqtt']['mqtt_topic']
        self.pir_id = pir_id
        self.mqtt_host = mqtt_host
        self.mqtt_topic = mqtt_topic

        self.sensor = 4

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.sensor, GPIO.IN, GPIO.PUD_DOWN)

        self.previous_state = False
        self.current_state = False
        self.previous_datetime = datetime.datetime.now()
        self.current_datetime = datetime.datetime.now()
        self.diagnosticCounter = 0

        print("Program started at %s" % datetime.datetime.now())
        print("-----------------------------------------------")
        print("pir ID    : %s" % self.pir_id)
        print("mqtt host : %s" % self.mqtt_host)
        print("mqtt topic: %s" % self.mqtt_topic)
        print("-----------------------------------------------")

    def mqtt_publish(self, msg, retain, v, ts):
        try:
            pubmsg = json.dumps({'devid':self.pir_id, 'msg': msg, 'v': v, 'ts': ts.isoformat()})
            publish.single(self.mqtt_topic, pubmsg, hostname=self.mqtt_host, retain=retain)
            publish.single(self.mqtt_topic + "/presence", v, hostname=self.mqtt_host, retain=retain)
            publish.single(self.mqtt_topic + "/message", msg, hostname=self.mqtt_host, retain=retain)
            publish.single(self.mqtt_topic + "/ts", ts.isoformat(), hostname=self.mqtt_host, retain=retain)
        except NameError as ne:
            print("Error with publish on mqtt: {0}", format(ne))
        except:
            print("Error with publish on mqtt: ", sys.exc_info()[0])

    def start(self):
        try:
            while True:
                time.sleep(0.1)
                ts = datetime.datetime.now()
                ts_str = ts.strftime('%Y-%m-%d_%H-%M-%S')

                self.diagnosticCounter += 1
                # if diagnosticCounter % (10*60) == 0:
                if self.diagnosticCounter % (10*5) == 0:
                    msg = "Nessuna presenza - %s " % ts_str
                    print(msg)
                    self.mqtt_publish(msg, False, 0, ts)
                    self.diagnosticCounter = 0

                previous_state = self.current_state
                # print("prev state %s, curr state %s" % (previous_state, current_state))
                self.current_state = GPIO.input(self.sensor)
                if self.current_state != previous_state:
                    new_state = "HIGH" if self.current_state else "LOW"

                    print("%s GPIO pin %s is %s" % (ts_str, self.sensor, new_state))

                    if new_state == "HIGH":
                        msg = "Presenza rilevata - %s" % ts_str
                        print(msg)
                        self.mqtt_publish(msg, False, 1, ts)
        finally:
            GPIO.cleanup()
            print("Program ended at %s" % datetime.datetime.now())
