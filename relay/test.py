import RPi.GPIO as GPIO
from time import sleep

relay_ch1 = 17
relay_ch2 = 18
relay_ch3 = 27
relay_ch4 = 22

# The script as below using BCM GPIO 00..nn numbers
GPIO.setmode(GPIO.BCM)

# Set relay pins as output
GPIO.setup(relay_ch1, GPIO.OUT)
GPIO.setup(relay_ch2, GPIO.OUT)
GPIO.setup(relay_ch3, GPIO.OUT)
GPIO.setup(relay_ch4, GPIO.OUT)

print("setup complete")

# Turn all relays ON
print("all on")
GPIO.output(relay_ch1, GPIO.HIGH)
GPIO.output(relay_ch2, GPIO.HIGH)
GPIO.output(relay_ch3, GPIO.HIGH)
GPIO.output(relay_ch4, GPIO.HIGH)
# Sleep for 5 seconds
sleep(5)


# Turn all relays OFF
print("all off")
GPIO.output(relay_ch1, GPIO.LOW)
GPIO.output(relay_ch2, GPIO.LOW)
GPIO.output(relay_ch3, GPIO.LOW)
GPIO.output(relay_ch4, GPIO.LOW)
# Sleep for 5 seconds
sleep(5)

# Turn all relays ON one by one
print("all on one by one")
GPIO.output(relay_ch1, GPIO.HIGH)
sleep(1)
GPIO.output(relay_ch2, GPIO.HIGH)
sleep(1)
GPIO.output(relay_ch3, GPIO.HIGH)
sleep(1)
GPIO.output(relay_ch4, GPIO.HIGH)
sleep(1)
# Sleep for 5 seconds
sleep(5)

# Turn all relays OFF one by one
print("all off one by one")
GPIO.output(relay_ch1, GPIO.LOW)
sleep(1)
GPIO.output(relay_ch2, GPIO.LOW)
sleep(1)
GPIO.output(relay_ch3, GPIO.LOW)
sleep(1)
GPIO.output(relay_ch4, GPIO.LOW)
sleep(1)
# Sleep for 5 seconds
sleep(5)

print("end")
GPIO.cleanup()