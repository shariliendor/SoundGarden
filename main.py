import threading
import time
from plant import Plant

#from scale_map import get_scale, get_note_list

def main():
    num_plants = 6
    # scale = get_note_list("C", "Major") TODO: scale stuff

    plant_names = ["Pothos(R)", "Pothos(L)", "Philodendron(R)", "Philodendron(L)", "Mini Monstera", "Arrowhead"]
    plant_list = []
    threads = []

    for i in range (num_plants+1):
        # initialize all the plant objects
        plant = Plant(name=plant_names[i-1])
        plant_list.append(plant)

        # initialize all the plant threads
        t = threading.Thread(
            target=plant.play_loop,
            args=(),
            name=f"Thread{i}",
        )
        threads.append(t)

    for t in threads:
        t.start() # warning: each thread runs indefinitely

    # change the scale after a bit
    time.sleep(10)
    for plant in plant_list:
        plant.set_scale(["D"])


if __name__ == "__main__":
    main()

# To run:
# source soundGardenVENV/bin/activate
# soundGardenVENV/bin/python3 main.py

