import threading
import time
from plant import Plant
from oscilloscope import PlantOscilloscope
import asyncio

from scale_map import get_scale, get_note_list
from audio_player import AudioPlayer

def main():
    num_plants = 6
    pause = 3           # the amount of time that a plant must wait before trying to play a new note
    threshold = 2       # proportion difference necessary to play a note
    interval_len = 20   # length of context window for comparing averages
    note_min = 1        # min times you'd prefer a plant to play per interval
    note_max = 10       # max times you'd prefer a plant to play per interval

    plant_names = ["Pothos(R)", "Pothos(L)", "Philodendron(R)", "Philodendron(L)", "Mini Monstera", "Arrowhead"]
    touch_pins = [18, 2, 3, 4, 5, 6] # placeholder vals
    plant_list = []
    threads = []

    for i in range (num_plants):
        # initialize all the plant objects
        plant = Plant(name=plant_names[i], 
                      pause=pause,
                      threshold=threshold, 
                      note_min=note_min, 
                      note_max=note_max, 
                      interval_len=interval_len,
                      touch_pin=touch_pins[i]
                    )
        plant_list.append(plant)

        # initialize all the plant threads
        t = threading.Thread(
            target=plant.play_loop,
            args=(),
            name=f"Thread{i}",
        )
        threads.append(t)

    for t in threads:
        t.start()

    #DURATION_SECONDS = 12 * 60 * 60
    DURATION_SECONDS = 20

    terrarium_wake_time = time.time()
    end_time = terrarium_wake_time + DURATION_SECONDS
    scale_change_start = time.time()
    oscilloscope_change_start = time.time()
    oscilloscope = PlantOscilloscope(plant_names, num_plants)
    update_vals = [0] * num_plants
    player = AudioPlayer()

    scale = asyncio.run(get_scale())
    for plant in plant_list:
        plant.set_scale(scale)

    # Loop that polls plants for a note to play and oscilloscope data
    # will use cron to run at 8 am every day? 
    while (time.time() < end_time):

        # change the scale after one hour
        if (time.time() - scale_change_start > 3600):
            scale_change_start = time.time()
            scale = asyncio.run(get_scale())
            for plant in plant_list:
                plant.set_scale(scale)

        for i in range(0, num_plants):
            plant = plant_list[i]
            if (plant.note != ""):
                print (plant.name, "is playing ", plant.note)
                try:
                    player.play_note(plant.note, duration=0.95)
                except ValueError as exc:
                    print(f"Could not play note from {plant.name}: {exc}")
                finally:
                    plant.clear_note()
                # eventually will send note to EQ
            update_vals[i] = 5000 - plant.curr_signal # subtract from oscilloscope y top to flip data

        # update the oscilloscope intermittently
        if (time.time() - oscilloscope_change_start > 0.04):
            oscilloscope_change_start = time.time()
            oscilloscope.update_plot(update_vals)        


    # end the threads
    for plant in plant_list:
        plant.playing = False

    # wait for all threads to wrap up
    for t in threads:
        t.join()

    player.close()
    print("stopped threads")

if __name__ == "__main__":
    main()

# To run:
# source soundGardenVENV/bin/activate
# soundGardenVENV/bin/python3 main.py

# or
# source .venv/bin/activate
# python main.py

# python -m pip install python_weather
