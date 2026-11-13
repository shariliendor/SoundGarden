import RPi.GPIO as GPIO
import time
import threading

# GPIO setup
GPIO.setmode(GPIO.BCM)

# Only allow one thread to access GPIO at a time
gpio_lock = threading.Lock()

def measure_bio_feedback(TOUCH_PIN=18):
    with gpio_lock:
        count = 0

        GPIO.setup(TOUCH_PIN, GPIO.OUT)
        GPIO.output(TOUCH_PIN, GPIO.LOW)

        time.sleep(0.1)

        GPIO.setup(TOUCH_PIN, GPIO.IN)

        while GPIO.input(TOUCH_PIN) == GPIO.LOW and count < 10000:
            count += 1

        return count
