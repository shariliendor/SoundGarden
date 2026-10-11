import time

class Plant:

    def __init__(self, name: str, pause: int, threshold=1.1, note_min=1, note_max=5, interval_len=10, ):
        # user set variables
        self.name = name
        self.pause = pause
        self.threshold = threshold
        self.interval_len = interval_len
        self.interval_arr = [0] * self.interval_len
        self.note_min = note_min
        self.note_max = note_max

        # used by main
        self._current_scale = ["C"] # dummy value
        self.playing = True
        self.note = ""
        self.curr_signal = 0

        # for statistical info
        self.iteration = 0
        self.average = 0
        self.past_avg = 0
        self.note_count = 0

        # for testing
        self.log_file = open("logs/top_leaf_electrode_log.txt", 'r')

    def set_scale(self, new_scale):
        self._current_scale = new_scale

    def clear_note(self):
        self.note = ""

    # play note with pitch, register, loudness, and duration
    def play_note(self, pitch: str, register: int, loudness: int, duration: int):
        print(self.name, "is playing", pitch)

    # loop that polls to play a note or not
    def play_loop(self):
        last_note_check = time.time()
        self.test_get_baselines()

        while self.playing:
            self.test_measure_bio_feedback()
            if (time.time() - last_note_check >= self.pause):
                if (self.note == ""):
                    self.determine_note()
                    last_note_check = time.time()

    # used to set the context if prev data doesn't exist yet
    def test_get_baselines(self):
        for i in range(0, self.interval_len):
            self.test_measure_bio_feedback()

    # determine what note to play, or null
    def determine_note(self):
        change = self.average / self.past_avg
        if change >= self.threshold:
            self.note = self._current_scale[0]
            self.note_count += 1
        else: print("did not play note")

    # simulated bio data for testing
    def test_measure_bio_feedback(self):
        if not self.log_file:
            return 0
        line = self.log_file.readline()
            
        measurements = [float(val) for val in line.strip().split() if val]
        self.curr_signal = measurements[0]
        
        if not measurements:
            return 0
                
        # Calculate the 1 second average
        second_average = sum(measurements) / len(measurements)
        self.average = int(round(second_average))

        # add the average to list
        self.interval_arr[self.iteration] = self.average
        self.iteration = (self.iteration + 1) % (self.interval_len)

        if self.iteration == 0:
            self.past_avg = sum(self.interval_arr) / self.interval_len
            if (self.note_count > self.note_max):
                self.threshold *= 1.1
                print("threshold increased")
            elif (self.note_count < self.note_min):
                self.threshold *= 0.9
                print("threshold decreased")
            self.note_count = 0

        time.sleep(0.1)
    