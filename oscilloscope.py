import matplotlib.pyplot as plt
from collections import deque

N = 100
num_plants = 8

# placeholder plant names
plant_names = ['Pothos1', 'Pothos2', 'Fittonia1', 'Fittonia2', 'Money Plant', 'Monstera', 'Fern1', 'Fern2']

plant_buffers = [deque([0]*N, maxlen=N) for i in range(num_plants)]

plt.ion()
fig, ax = plt.subplots()
fig.subplots_adjust(left=0.15) # some padding for left-hand side

lines = []
linestyles = ['-', '--', '-.', ':']
for i in range(num_plants):
    line, = ax.plot(plant_buffers[i], linestyle=linestyles[i % len(linestyles)], label=plant_names[i])
    lines.append(line)

# different legend options:
# ax.legend(loc='upper right') fixes the legend to the right corner
# ax.legend() automatically adjusts to best position but jumps around often
# custom legend:
ax.legend(
    loc='lower center',
    bbox_to_anchor=(0.5, 1.1),
    ncol=num_plants,
    fontsize=8,
    handlelength=1.2,
    handletextpad=0.3,
    columnspacing=0.8,
    frameon=False
)

fig.subplots_adjust(top=0.85)
ax.set_ylim(0, 100000)
ax.set_title("Bioelectric Signal (Touch Sensor)")
ax.set_ylabel("Charge Time (Proxy for Voltage)")
ax.set_xlabel("Time (samples)")

"""
Updates all plant lines in the plot
values : an array of integers representing the updated plant reading values
Note: the plants are identified by index position in array
"""
def update_plot(values):
    for i, val in enumerate(values):
        plant_buffers[i].append(val)
        lines[i].set_ydata(plant_buffers[i])
        lines[i].set_xdata(range(len(plant_buffers[i])))
    plt.pause(0.01)
    

"""
# fake plant data for testing
import random
import math
import time

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

def generate_plant_data():
    while True:
        fake_values = get_fake_values()
        update_plot(fake_values)
        time.sleep(0.01)

generate_plant_data()
"""

# to run, do once:
# python3 -m venv venv && source venv/bin/activate && pip install matplotlib
# then:
# source venv/bin/activate
# python oscilloscope.py