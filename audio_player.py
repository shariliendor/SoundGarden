import threading
from pathlib import Path

import fluidsynth


# SoundFont path (system-wide installation).
SOUNDFONT_PATH = Path("/usr/share/sounds/sf2/FluidR3_GM.sf2")

# Audio configuration for Raspberry Pi 5.
SAMPLE_RATE = 44100
AUDIO_DRIVER = "alsa"
AUDIO_DEVICE = "default"

# Default volume (0.0 to 1.0).
DEFAULT_VOLUME = 0.7

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

    def __init__(self, volume=DEFAULT_VOLUME):

        if not SOUNDFONT_PATH.is_file():
            raise FileNotFoundError(
                f"SoundFont not found: {SOUNDFONT_PATH}"
            )

        if not 0.0 <= volume <= 1.0:
            raise ValueError("Volume must be between 0.0 and 1.0")

        self.lock = threading.RLock()
        self.timers = set()
        self.closed = False

        self.synth = None
        self.soundfont_id = None

        try:
            # Initialize FluidSynth.
            self.synth = fluidsynth.Synth(
                gain=volume,
                samplerate=SAMPLE_RATE,
            )

            # Initialize Raspberry Pi audio output.
            self.synth.start(
                driver=AUDIO_DRIVER,
                device=AUDIO_DEVICE,
            )

            # Load SoundFont.
            self.soundfont_id = self.synth.sfload(
                str(SOUNDFONT_PATH)
            )

            if self.soundfont_id == -1:
                raise RuntimeError(
                    "FluidSynth could not load the SoundFont"
                )

            # Bank 0, preset 0: General MIDI piano.
            self.synth.program_select(
                0,
                self.soundfont_id,
                0,
                0,
            )

            print("Raspberry Pi Audio Player initialized.")
            print(f"SoundFont: {SOUNDFONT_PATH}")
            print(f"Audio driver: {AUDIO_DRIVER}")
            print(f"Audio device: {AUDIO_DEVICE}")

        except Exception:
            if self.synth is not None:
                self.synth.delete()
                self.synth = None
            raise

    def play_note(self, note, duration=0.35, velocity=90):
        """
        Play a musical note.

        Examples:
            player.play_note("C")
            player.play_note("A#", duration=1.0)
            player.play_note("F#", duration=0.5)
        """

        note = note.strip().upper()

        if note not in NOTE_TO_MIDI:
            raise ValueError(
                f"Unsupported note: {note!r}. "
                f"Expected one of {list(NOTE_TO_MIDI)}"
            )

        if duration <= 0:
            raise ValueError("Duration must be greater than zero")

        if not 0 <= velocity <= 127:
            raise ValueError("Velocity must be between 0 and 127")

        midi_note = NOTE_TO_MIDI[note]

        with self.lock:

            if self.closed:
                return

            self.synth.noteon(
                0,
                midi_note,
                velocity,
            )

            # Create an independent timer for each note event.
            timer = threading.Timer(
                duration,
                self._stop_note,
                args=(midi_note,),
            )

            self.timers.add(timer)
            timer.start()

        print(f"Playing {note} (MIDI {midi_note})")

    def _stop_note(self, midi_note):

        with self.lock:

            if not self.closed:
                self.synth.noteoff(
                    0,
                    midi_note,
                )

            # Remove completed timer.
            current = threading.current_thread()
            self.timers.discard(current)

    def close(self):

        with self.lock:

            if self.closed:
                return

            self.closed = True

            # Cancel pending note timers.
            for timer in list(self.timers):
                timer.cancel()

            self.timers.clear()

            # Stop all remaining notes.
            if self.synth is not None:
                self.synth.all_sounds_off(0)
                self.synth.delete()
                self.synth = None

            print("Audio Player shut down.")