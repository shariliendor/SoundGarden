import time
import random
import math
from oscilloscope import PlantOscilloscope

plant_names = ['Pothos1', 'Pothos2', 'Fittonia1', 'Fittonia2', 'Money Plant', 'Monstera', 'Fern1', 'Fern2']

num_plants = 8
oscillo = PlantOscilloscope(plant_names, num_plants)


def get_fake_values():
    t = time.time()
    values = []
    for i in range(num_plants):
        baseline = 30000 + 10000 * math.sin(0.05 * t + i)
        spike = 0
        if random.random() < 0.02:
            spike = random.randint(10000, 40000)
        value = baseline + spike
        values.append(value)
    return values


while True:
    fake_values = get_fake_values()
    oscillo.update_plot(fake_values)

# to run, do once:
# python3 -m venv venv && source venv/bin/activate && pip install matplotlib
# then:
# source venv/bin/activate
# python oscilloscope_test.py