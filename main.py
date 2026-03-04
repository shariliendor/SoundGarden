import random
import asyncio
import time
from plant import Plant
from scale_map import get_scale, get_note_list

async def main() -> None:

    # get the scale
    # eventually want to put this in the while loop so it updates when it needs to
    # maybe update periodically every 10 minutes or something
    # scale = await get_scale()
    scale = get_note_list("C", "Major")

    # Set up some dummy plants
    plants: list[Plant] = []
    for i in range(5):
        new_plant = Plant("plant " + str(i))
        plants.append(new_plant)

    while True:
        for plant in plants:
            if plant.get_signal():
                note = random.choice(scale)
                plant.play_note(note, 1, 2, 3)

if __name__ == "__main__":
    asyncio.run(main())