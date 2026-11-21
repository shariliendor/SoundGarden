import sys
import time
import signal
import numpy as np
import pyaudio

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QGuiApplication, QKeySequence
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QShortcut

import pyqtgraph as pg


# --- CONFIGURATION PARAMETERS ---
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
UPDATE_MS = 20

SILENCE_FLOOR_DB = -60
FULL_LEVEL_DB = -30

DISPLAY_ATTACK_SECONDS = 0.05
DISPLAY_RELEASE_SECONDS = 1.5

# Second display configuration
SECOND_DISPLAY_X = 0
SECOND_DISPLAY_Y = 0


class AudioEQVisualizer(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Real-Time System Audio EQ Visualizer")

        # Central widget layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QtWidgets.QVBoxLayout(self.central_widget)

        # Create pyqtgraph PlotWidget
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)

        # Configure plot appearance
        self.plot_widget.setBackground('k')
        self.plot_widget.setYRange(0, 80)
        self.plot_widget.setLabel('left', 'Magnitude', units='dB')
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

        # Initialize green EQ curve
        self.curve = self.plot_widget.plot(
            pen=pg.mkPen('g', width=2)
        )

        # Frequency bin mappings
        self.frequencies = np.fft.rfftfreq(
            CHUNK,
            d=1.0 / RATE
        )

        self.plot_widget.setXRange(0, 20000)

        self.display_magnitude = np.zeros_like(
            self.frequencies
        )

        self.last_update_time = time.monotonic()

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        self.stream = None
        self.audio_closed = False

        # Find loopback or monitor device
        device_index = None

        print("--- Scanning Audio Input Devices ---")

        for i in range(self.p.get_device_count()):

            dev = self.p.get_device_info_by_index(i)

            print(
                f"Device {i}: {dev['name']} "
                f"(Channels: {dev['maxInputChannels']})"
            )

            if any(
                k in dev['name'].lower()
                for k in ["loopback", "monitor", "output.monitor"]
            ):
                device_index = i

        if device_index is not None:

            print(
                f"\n--> Selected Device Index {device_index} "
                "for system audio loopback capture."
            )

        else:

            print(
                "\n--> No explicit loopback device detected. "
                "Using system default input device."
            )

            print(
                "    (Note: You may need to create a loopback "
                "device or use PulseAudio/PipeWire volume control "
                "to route system audio.)"
            )

        # Open audio stream
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )

        # Setup refresh timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(UPDATE_MS)

        # Keyboard shortcuts that work even when graph has focus
        self.escape_shortcut = QShortcut(
            QKeySequence(Qt.Key_Escape), self
        )
        self.escape_shortcut.activated.connect(self.close)

        self.quit_shortcut = QShortcut(
            QKeySequence("Q"), self
        )
        self.quit_shortcut.activated.connect(self.close)

    def keyPressEvent(self, event):

        if event.key() in (Qt.Key_Escape, Qt.Key_Q):

            print("Closing audio visualizer...")

            self.close()
            return

        super().keyPressEvent(event)

    def update_plot(self):

        try:

            data = self.stream.read(
                CHUNK,
                exception_on_overflow=False
            )

            signal_data = np.frombuffer(
                data,
                dtype=np.int16
            ).astype(np.float32)

            # Calculate RMS input level
            rms = np.sqrt(np.mean(signal_data ** 2))

            level_db = 20 * np.log10(
                max(rms / 32768, 1e-12)
            )

            fade = np.clip(
                (level_db - SILENCE_FLOOR_DB) /
                (FULL_LEVEL_DB - SILENCE_FLOOR_DB),
                0,
                1,
            )

            attenuation = fade * fade * (3 - 2 * fade)

            # Apply Hanning window
            windowed_signal = (
                signal_data * np.hanning(len(signal_data))
            )

            # Calculate FFT
            fft_data = np.fft.rfft(windowed_signal)

            magnitude = np.abs(fft_data)

            log_magnitude = 20 * np.log10(magnitude + 1)

            target_magnitude = log_magnitude * attenuation

            # Smooth display
            now = time.monotonic()

            elapsed = now - self.last_update_time

            self.last_update_time = now

            attack = 1 - np.exp(
                -elapsed / DISPLAY_ATTACK_SECONDS
            )

            release = 1 - np.exp(
                -elapsed / DISPLAY_RELEASE_SECONDS
            )

            smoothing = np.where(
                target_magnitude < self.display_magnitude,
                release,
                attack,
            )

            self.display_magnitude += (
                target_magnitude - self.display_magnitude
            ) * smoothing

            # Update graph
            self.curve.setData(
                self.frequencies,
                self.display_magnitude
            )

        except Exception:
            # Ignore dropped frame exceptions
            pass

    def closeEvent(self, event):

        # Stop refresh timer
        self.timer.stop()

        # Clean up audio resources only once
        if not self.audio_closed:

            self.audio_closed = True

            try:

                if self.stream is not None:

                    if self.stream.is_active():
                        self.stream.stop_stream()

                    self.stream.close()

            except Exception as exc:
                print(f"Audio stream cleanup error: {exc}")

            try:
                self.p.terminate()

            except Exception as exc:
                print(f"PyAudio cleanup error: {exc}")

        event.accept()


def main():

    app = QtWidgets.QApplication(sys.argv)

    visualizer = AudioEQVisualizer()

    # Allow SIGTERM from main.py to close the window cleanly
    signal.signal(
        signal.SIGTERM,
        lambda signum, frame: QtCore.QTimer.singleShot(
            0,
            visualizer.close
        )
    )

    # Get available displays
    screens = QGuiApplication.screens()

    print("\n--- Detected Displays ---")

    for i, screen in enumerate(screens):

        print(
            f"Display {i}: {screen.name()} "
            f"{screen.geometry().getRect()}"
        )

    # Find the second display using its expected coordinates
    second_screen = None

    for screen in screens:

        geometry = screen.geometry()

        if (
            geometry.x() <= SECOND_DISPLAY_X < geometry.x() + geometry.width()
            and geometry.y() <= SECOND_DISPLAY_Y < geometry.y() + geometry.height()
        ):
            second_screen = screen
            break

    # Fallback to second detected display
    if second_screen is None and len(screens) >= 2:

        second_screen = screens[1]

    if second_screen is not None:

        print(
            f"\nOpening fullscreen visualizer on: "
            f"{second_screen.name()}"
        )

        # Move window to second display before fullscreen
        visualizer.setGeometry(
            second_screen.geometry()
        )

    else:

        print(
            "\nWARNING: Second display not detected!"
        )

        print(
            "Opening fullscreen visualizer on primary display."
        )

        visualizer.setGeometry(
            screens[0].geometry()
        )

    # Automatically enter fullscreen
    visualizer.showFullScreen()

    print("\nAudio EQ visualizer running fullscreen.")
    print("Press ESC or Q to exit.")

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
