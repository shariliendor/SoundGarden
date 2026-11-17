import threading
import time
import asyncio
import subprocess
import os
import sys

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

from plant import Plant
from oscilloscope import PlantOscilloscope
from scale_map import get_scale, get_note_list
from audio_player import AudioPlayer


def main():
    num_plants = 6
    pause = 2           # The amount of time a plant must wait before trying to play a new note
    threshold = 1.2     # Proportion difference necessary to play a note
    interval_len = 10   # Length of context window for comparing averages
    note_min = 1        # Minimum times you'd prefer a plant to play per interval
    note_max = 5        # Maximum times you'd prefer a plant to play per interval

    plant_names = [
        "Pothos",
        "Alocasia",
        "African Violet",
        "Philodendron",
        "Peperomia",
        "Monstera"
    ]

    # Zero-based General MIDI programs: piano, music box, nylon guitar,
    # acoustic bass, harp, and flute.
    plant_instruments = [53, 10, 24, 32, 46, 73]

    touch_pins = [18, 23, 24, 25, 17, 27]
    for pin in touch_pins:
        GPIO.setup(pin, GPIO.IN)

    plant_list = []
    threads = []

    oscilloscope = PlantOscilloscope(plant_names, num_plants)

    for i in range(num_plants):
        # Initialize all the plant objects
        plant = Plant(
            name=plant_names[i],
            pause=pause,
            threshold=threshold,
            note_min=note_min,
            note_max=note_max,
            interval_len=interval_len,
            touch_pin=touch_pins[i],
            instrument=plant_instruments[i],
        )

        plant_list.append(plant)

        # Initialize all the plant threads
        t = threading.Thread(
            target=plant.play_loop,
            args=(),
            name=f"Thread{i}",
        )

        threads.append(t)

    for t in threads:
        t.start()

    #DURATION_SECONDS = 12 * 60 * 60  # 12 hours
    DURATION_SECONDS = 60

    terrarium_wake_time = time.time()
    end_time = terrarium_wake_time + DURATION_SECONDS

    scale_change_start = time.time()
    oscilloscope_change_start = time.time()

    update_vals = [0] * num_plants
    player = AudioPlayer()

    # Launch the audio EQ visualizer on the second display
    visualizer_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "visualizer.py"
    )

    visualizer_process = subprocess.Popen(
        [sys.executable, visualizer_path]
    )

    print("Audio EQ visualizer launched")

    try:
        scale = asyncio.run(get_scale())

        for plant in plant_list:
            plant.set_scale(scale)

        # Loop that polls plants for a note to play and oscilloscope data
        # Will eventually use cron to run at 8 am every day?
        while time.time() < end_time:

            # Change the scale after one hour
            if time.time() - scale_change_start > 3600:
                scale_change_start = time.time()
                scale = asyncio.run(get_scale())

                for plant in plant_list:
                    plant.set_scale(scale)

            for i in range(num_plants):
                plant = plant_list[i]

                if plant.note != "" and plant.curr_signal != 10000:
                    print(plant.name, "is playing", plant.note)

                    try:
                        player.play_note(
                            plant.note,
                            duration=0.95,
                            instrument=plant.instrument,
                            channel=i,
                        )

                    except ValueError as exc:
                        print(f"Could not play note from {plant.name}: {exc}")

                    finally:
                        plant.clear_note()

                # Subtract from oscilloscope y top to flip data
                #update_vals[i] = max(500, min(5000 - plant.curr_signal, 4500))
                update_vals[i] = max(0, min(5000 - plant.curr_signal, 5000))

            # Update the oscilloscope intermittently
            if time.time() - oscilloscope_change_start > 0.1:
                oscilloscope_change_start = time.time()
                oscilloscope.update_plot(update_vals)

            time.sleep(0.005)

    finally:
        # End the threads
        for plant in plant_list:
            plant.playing = False

        # Wait for all threads to wrap up
        for t in threads:
            t.join()

        player.close()

        # Stop the EQ visualizer
        if visualizer_process.poll() is None:
            print("Stopping EQ visualizer...")

            visualizer_process.terminate()

            try:
                visualizer_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                visualizer_process.kill()
                visualizer_process.wait()

        GPIO.cleanup()

        print("stopped threads")


if __name__ == "__main__":
    main()


# To run:
# source soundGardenVENV/bin/activate
# soundGardenVENV/bin/python3 main.py

# Or:
# source .venv/bin/activate
# python main.py