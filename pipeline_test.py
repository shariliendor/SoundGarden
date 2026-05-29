from measure_capacitance import measure_bio_feedback
from oscilloscope import PlantOscilloscope
import time

print("this is the script I want")

def get_log_str(measurements):
    log_str = ""
    result = ' '.join(str(m) for m in measurements)
    return result

initial_time = time.time()
time_interval = 1 #time passed for one sublist of measurements in the log
second_counter = 0; #keeps track of how many seconds have passed

average_interval = 30; #is the number of seconds that pass before reseting the second counter
average_total = 0; #current total of the second averages over the last average_interval amount of seconds

second_total = 0; #total of the measurements within a single second
second_measurement_count = 0; #number of measurements taken within this second

last_average = 0; #average of the previous average_interval # of seconds

# a log of values, each sublist contains the measurements taken within the ith time
# interval since initial_time
log = [[]]

plant_names = ["test"]
#oscillo = PlantOscilloscope(plant_names, len(plant_names), 100)

while True:
    # take the measurement and send it to the oscilloscope
    measurement = measure_bio_feedback()
    second_total += measurement
    second_measurement_count += 1
    #measurement = 1000
    #time.sleep(0.1)
    #oscillo.update_plot([measurement])

    # log the measurement and add a new sublist if needed
    log[-1].append(measurement)

    time_intervals_since_start = (time.time() - initial_time) / time_interval
    if time_intervals_since_start > len(log):
        #print(log[-1])

        with open("charlie_log.txt", 'a') as log_file:
            second_average = round(second_total/second_measurement_count, 4)
            if(second_counter < average_interval):
                second_counter += 1
                average_total += second_average
            else:
                second_counter = 1
                
                interval_average = round(average_total/average_interval, 4)
                
                print(f"Previous {average_interval} second average: {last_average}")
                print(f"Current {average_interval} second average: {interval_average}")
                
                
                
                if(last_average < interval_average):
                    percent_difference = round((abs(last_average - interval_average) / ((last_average + interval_average)/2)) * 100, 2)
                    print(f"{percent_difference} larger")
                elif(last_average > interval_average):
                    percent_difference = round((abs(last_average - interval_average) / ((last_average + interval_average)/2)) * 100, 2)
                    print(f"{percent_difference} smaller")
                else:
                    percent_difference = 0;
                    print(f"Previous {average_interval} second average, and Current {average_interval} second average are identical")
                    
                #clean up our variables for the next interval of seconds
                last_average = interval_average;
                average_total = 0
                average_total += second_average

            log_str = get_log_str(log[-1])
            print(f"{second_counter}", log_str, f"Average: {second_average}")
            log_file.write(log_str + '\n')
            second_total = 0
            second_measurement_count = 0

        log.append([])

