import threading
import time
from plant import Plant

# from scale_map import get_scale, get_note_list

def main():
    num_plants = 6
    pause_interval = 10
    # scale = get_note_list("C", "Major") TODO: scale stuff

    plant_names = ["Pothos(R)", "Pothos(L)", "Philodendron(R)", "Philodendron(L)", "Mini Monstera", "Arrowhead"]
    plant_list = []
    threads = []

    for i in range (num_plants):
        # initialize all the plant objects
        plant = Plant(name=plant_names[i], pause=pause_interval)
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

    # Loop that polls plants for a note to play
    playing_start = time.time()
    scale_change_start = time.time()
    while (time.time() - playing_start < 30): # only lasts 30 sec for testing

        # change the scale after a certain time interval (one hour in final code)
        if (time.time() - scale_change_start > 20):
            scale_change_start = time.time()
            for plant in plant_list:
                plant.set_scale(["D"])

        for plant in plant_list:
            if (plant.note != ""):
                print (plant.name, "is playing ", plant.note)
                plant.clear_note()
                # eventually will send note to audio system and EQ
        
        # eventually will send measurement info to oscilloscope
        


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

