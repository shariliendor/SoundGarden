import fluidsynth
import RPi.GPIO as GPIO
import time
import random

# Setup FluidSynth
fs = fluidsynth.Synth()
fs.start(driver="alsa")  # Use ALSA driver on Raspberry Pi

# Load General MIDI soundfont
soundfont_id = fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
fs.program_select(0, soundfont_id, 0, 0)  # Channel 0, piano sound

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

def play_random_note():
    pitch = random.randint(60, 80)  # MIDI notes between middle C and high notes
    velocity = random.randint(40, 100)
    duration = random.uniform(0.2, 1.0)

    print(f"Playing note: pitch={pitch}, velocity={velocity}, duration={duration:.2f}s")
    fs.noteon(0, pitch, velocity)
    time.sleep(duration)
    fs.noteoff(0, pitch)

try:
    while True:
        bio_signal = measure_bio_feedback()
        print("Plant bioelectric measurement:", bio_signal)

        # Adjust threshold based on your plant's typical measurements
        if bio_signal < 50000:
            play_random_note()
        else:
            print("No note triggered.")

        time.sleep(1.0)

except KeyboardInterrupt:
    print("\nCleaning up...")
    GPIO.cleanup()
    fs.delete()