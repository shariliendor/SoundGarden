import random

class Plant:

    def __init__(self, name: str):
        self.name = name

    # play note with pitch, register, loudness, and duration
    def play_note(self, pitch: str, register: int, loudness: int, duration: int):
        print(self.name, "is playing", pitch)

    # returns true if a spike is happening, false if not
    def get_signal(self):
        # for now just a 1/10 chance for a spike
        # in the future, we'll analyze the signal to figure this out
        return random.randint(0, 10) == 1