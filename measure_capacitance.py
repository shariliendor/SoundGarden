import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
TOUCH_PIN = 18

def measure_bio_feedback():
    count = 0
    GPIO.setup(TOUCH_PIN, GPIO.OUT)
    GPIO.output(TOUCH_PIN, GPIO.LOW)
    time.sleep(0.1)
    GPIO.setup(TOUCH_PIN, GPIO.IN)

    while GPIO.input(TOUCH_PIN) == GPIO.LOW and count < 100000:
        count += 1
    return count
