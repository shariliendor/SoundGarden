import threading
import time
from plant import Plant
from oscilloscope import PlantOscilloscope

# from scale_map import get_scale, get_note_list

def main():
    num_plants = 6
    pause = 5           # the amount of time that a plant must wait before trying to play a new note
    threshold = 1.5     # proportion difference necessary to play a note
    interval_len = 20   # length of context window for comparing averages
    note_min = 1        # min times you'd prefer a plant to play per interval
    note_max = 3        # max times you'd prefer a plant to play per interval

    # scale = get_note_list("C", "Major") TODO: scale stuff

    plant_names = ["Pothos(R)", "Pothos(L)", "Philodendron(R)", "Philodendron(L)", "Mini Monstera", "Arrowhead"]
    plant_list = []
    threads = []

    for i in range (num_plants):
        # initialize all the plant objects
        plant = Plant(name=plant_names[i], 
                      pause=pause,
                      threshold=threshold, 
                      note_min=note_min, 
                      note_max=note_max, 
                      interval_len=interval_len
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

    # Loop that polls plants for a note to play and oscilloscope data
    playing_start = time.time()
    scale_change_start = time.time()
    oscilloscope_change_start = time.time()
    oscilloscope = PlantOscilloscope(plant_names, num_plants)

    # will need to modify so this loop cycles on and off every 12 hours
    while (time.time() - playing_start < 60):
        update_vals = [0] * num_plants

        # change the scale after a certain time interval (one hour in final code)
        if (time.time() - scale_change_start > 20):
            scale_change_start = time.time()
            for plant in plant_list:
                plant.set_scale(["D"])

        for i in range(0, num_plants):
            plant = plant_list[i]
            if (plant.note != ""):
                print (plant.name, "is playing ", plant.note)
                plant.clear_note()
                # eventually will send note to audio system and EQ
            update_vals[i] = plant.curr_signal

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

    print("stopped threads")

if __name__ == "__main__":
    main()

# To run:
# source soundGardenVENV/bin/activate
# soundGardenVENV/bin/python3 main.py

