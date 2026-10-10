# gpio_trigger.py
import RPi.GPIO as GPIO
import time
import sys

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

try:
    while True:
        bio_signal = measure_bio_feedback()
        if bio_signal < 50000:
            print("TRIGGER")
            sys.stdout.flush()
        time.sleep(1.0)

except KeyboardInterrupt:
    GPIO.cleanup()