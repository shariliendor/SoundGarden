# music_player.py
import fluidsynth
import random
import sys
import time

fs = fluidsynth.Synth()
fs.start(driver="alsa")

sfid = fs.sfload("/usr/share/sounds/sf2/FluidR3_GM.sf2")
fs.program_select(0, sfid, 0, 0)

def play_random_note():
    pitch = random.randint(60, 80)
    velocity = random.randint(50, 100)
    duration = random.uniform(0.2, 1.0)
    print(f"Playing: {pitch}, vel={velocity}, dur={duration:.2f}s")
    fs.noteon(0, pitch, velocity)
    time.sleep(duration)
    fs.noteoff(0, pitch)

try:
    while True:
        line = sys.stdin.readline().strip()
        if line == "TRIGGER":
            play_random_note()

except KeyboardInterrupt:
    fs.delete()