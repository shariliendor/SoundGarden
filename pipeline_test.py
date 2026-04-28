#from touchActivatedSignal import measure_bio_feedback
from oscilloscope import PlantOscilloscope
import time

initial_time = time.time()
time_interval = 1 # time passed for one sublist of measurements in the log

# a log of values, each sublist contains the measurements taken within the ith time
# interval since initial_time
log = [[]]

plant_names = ["test"]
oscillo = PlantOscilloscope(plant_names, len(plant_names), 100)

while True:
    # take the measurement and send it to the oscilloscope
    #measurement = measure_bio_feedback()
    measurement = 1000
    time.sleep(0.1)
    oscillo.update_plot([measurement])

    # log the measurement and add a new sublist if needed
    log[-1].append(measurement)

    time_intervals_since_start = (time.time() - initial_time) / time_interval
    if time_intervals_since_start > len(log):
        print(log[-1])
        log.append([])

