#this program is used to test the GPIO outputs of the raspberry pi

import RPi.GPIO as GPIO
import time

#configure board pin layout
GPIO.setmode(GPIO.BCM)

#initialize pins
status_led = 4
GPIO.setup(status_led, GPIO.OUT)
GPIO.output(status_led, 1)
status_flag = 1

#run program
while True:
    time.sleep(3)
    if status_flag:
        GPIO.output(status_led, 0)
        status_flag = 0
        print ('turning LED off')
	continue
    else:
        GPIO.output(status_led, 1)
        status_flag = 1
	print ('turning LED on')
        continue

