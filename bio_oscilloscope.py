import RPi.GPIO as GPIO
import time
import matplotlib.pyplot as plt
from collections import deque

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

# Rolling buffer of last N readings
N = 100
signal_data = deque([0]*N, maxlen=N)

plt.ion()  # Interactive mode on
fig, ax = plt.subplots()
line, = ax.plot(signal_data)
ax.set_ylim(0, 100000)
ax.set_title("Bioelectric Signal (Touch Sensor)")
ax.set_ylabel("Charge Time (Proxy for Voltage)")
ax.set_xlabel("Time (samples)")

try:
    while True:
        signal = measure_bio_feedback()
        signal_data.append(signal)

        line.set_ydata(signal_data)
        line.set_xdata(range(len(signal_data)))
        ax.relim()
        ax.autoscale_view(scaley=True)
        plt.pause(0.01)

except KeyboardInterrupt:
    GPIO.cleanup()
    plt.close()