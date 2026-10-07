import threading
import time
from plant import Plant

# from scale_map import get_scale, get_note_list

def main():
    num_plants = 6
    # scale = get_note_list("C", "Major") TODO: scale stuff

    plant_names = ["Pothos(R)", "Pothos(L)", "Philodendron(R)", "Philodendron(L)", "Mini Monstera", "Arrowhead"]
    plant_list = []
    threads = []

    for i in range (num_plants):
        # initialize all the plant objects
        plant = Plant(name=plant_names[i])
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

    # change the scale after a bit
    time.sleep(10)
    for plant in plant_list:
        plant.set_scale(["D"])

    # end the threads after another little bit
    time.sleep(10)
    for plant in plant_list:
        plant.playing = False

    # wait for all threads to wrap up
    # TODO: we'll have to decide whether to end the threads each 12 hour period or just pause them
    for t in threads:
        t.join()

    print("testing stopping threads")

if __name__ == "__main__":
    main()

# To run:
# source soundGardenVENV/bin/activate
# soundGardenVENV/bin/python3 main.py

