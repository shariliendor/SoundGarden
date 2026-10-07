import random
import time

class Plant:

    def __init__(self, name: str):
        self.name = name
        self._current_scale = ["C"] # dummy value
        self.playing = True

    def set_scale(self, new_scale):
        self._current_scale = new_scale


    # play note with pitch, register, loudness, and duration
    def play_note(self, pitch: str, register: int, loudness: int, duration: int):
        print(self.name, "is playing", pitch)

    # play loop prototype. Currently 1/10 chance plays a note, then random 0 to 5 sec sleep
    def play_loop(self):
        while self.playing:
            play_note = self.get_signal()
            if play_note:
                print(self.name, "is playing", self._current_scale[0]) # TODO: actually implement this
            sleep = random.randint(0, 5)
            time.sleep(sleep)

    # testing timing and synchronization
    def second_test(self):
        while self.playing:
            start = time.time()
            print(self.name, " 1 sec")
            end = time.time()
            elapsed = end - start
            if elapsed < 1:
                time.sleep(1-elapsed)
        

    # returns true if a spike is happening, false if not
    def get_signal(self):
        # for now just a 1/10 chance for a spike
        # in the future, we'll analyze the signal to figure this out
        return random.randint(0, 10) == 1