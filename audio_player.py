
# audio player prototype for testing on mac
import threading
from pathlib import Path

import fluidsynth


# SoundFont path relative to this Python file, not the terminal directory.
SOUNDFONT_PATH = (
    Path(__file__).resolve().parent
    / "assets"
    / "soundfonts"
    / "FluidR3_GM.sf2"
)

# MIDI pitch numbers for octave 4.
NOTE_TO_MIDI = {
    "C": 60,
    "C#": 61,
    "D": 62,
    "D#": 63,
    "E": 64,
    "F": 65,
    "F#": 66,
    "G": 67,
    "G#": 68,
    "A": 69,
    "A#": 70,
    "B": 71,
}


class AudioPlayer:
    def __init__(self, volume=0.7):
        if not SOUNDFONT_PATH.is_file():
            raise FileNotFoundError(
                f"SoundFont not found: {SOUNDFONT_PATH}"
            )

        self.synth = fluidsynth.Synth(
            gain=volume,
            samplerate=44100,
        )
        self.synth.start(driver="coreaudio")

        self.soundfont_id = self.synth.sfload(
            str(SOUNDFONT_PATH)
        )

        if self.soundfont_id == -1:
            self.synth.delete()
            raise RuntimeError("FluidSynth could not load the SoundFont")

        # Bank 0, preset 0: typically the General MIDI piano.
        self.synth.program_select(
            0, self.soundfont_id, 0, 0
        )

        self.lock = threading.Lock()
        self.timers = []
        self.closed = False

    def play_note(self, note, duration=0.35, velocity=90):
        """Play a note name such as C, A#, or F#."""

        note = note.strip().upper()

        if note not in NOTE_TO_MIDI:
            raise ValueError(
                f"Unsupported note: {note!r}. "
                f"Expected one of {list(NOTE_TO_MIDI)}"
            )

        midi_note = NOTE_TO_MIDI[note]

        with self.lock:
            if self.closed:
                return

            self.synth.noteon(0, midi_note, velocity)

            # Release the note later without blocking the caller.
            timer = threading.Timer(
                duration, self._stop_note, args=(midi_note,)
            )
            self.timers.append(timer)
            timer.start()

        print(f"Playing {note} (MIDI {midi_note})")

    def _stop_note(self, midi_note):
        with self.lock:
            if not self.closed:
                self.synth.noteoff(0, midi_note)

    def close(self):
        with self.lock:
            self.closed = True

            for timer in self.timers:
                timer.cancel()

            self.timers.clear()
            self.synth.delete()
