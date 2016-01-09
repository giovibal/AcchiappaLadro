import RPi.GPIO as GPIO
import time
import datetime
import paho.mqtt.publish as publish

sensor = 4

GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor, GPIO.IN, GPIO.PUD_DOWN)

previous_state = False
current_state = False

previous_datetime = datetime.datetime.now()
current_datetime = datetime.datetime.now()

while True:
    time.sleep(0.1)
    previous_state = current_state
    current_state = GPIO.input(sensor)
    if current_state != previous_state:
        new_state = "HIGH" if current_state else "LOW"

        ts_str = datetime.datetime.now()
        print("%s GPIO pin %s is %s" % (ts_str, sensor, new_state))
         
        # publish on mqt /baleani/laspio/pir1
        if new_state == "HIGH":
            current_datetime = datetime.datetime.now()
            time_delta = current_datetime - previous_datetime
            previous_datetime = current_datetime
            msg = "Presenza rilevata - %s (%s tempo passato: %s)" % (ts_str, new_state, time_delta)
        else:
            current_datetime = datetime.datetime.now()
            time_delta = current_datetime - previous_datetime
            previous_datetime = current_datetime

            msg = "Nessuno - %s (%s tempo passato: %s)" % (ts_str, new_state, time_delta)

        publish.single("/baleani/laspio/pir1", msg, hostname="iot.eclipse.org", retain=True)

print("Closing pirtest2 session ...");

