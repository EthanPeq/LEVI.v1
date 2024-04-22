import RPi.GPIO as GPIO

red_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(red_pin, GPIO.OUT)

GPIO.output(red_pin,GPIO.HIGH)
