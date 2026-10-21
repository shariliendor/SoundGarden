import sys
import numpy as np
import pyaudio
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg

# --- CONFIGURATION PARAMETERS ---
FORMAT = pyaudio.paInt16
CHANNELS = 1              # Mono capturing is cleanest for EQ calculation
RATE = 44100              # Sampling rate in Hz
CHUNK = 1024              # Buffer frames (lower = lower latency, higher = better frequency resolution)
UPDATE_MS = 20            # Plot refresh interval in milliseconds (~50 FPS)

class AudioEQVisualizer(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize UI window
        self.setWindowTitle("Real-Time System Audio EQ Visualizer")
        self.resize(800, 400)
        
        # Central widget layout
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        
        # Create a pyqtgraph PlotWidget for high-performance hardware rendering
        self.plot_widget = pg.PlotWidget()
        self.layout.addWidget(self.plot_widget)
        
        # Configure plot appearance
        self.plot_widget.setBackground('k')  # Black background
        self.plot_widget.setYRange(0, 80)    # Decibel magnitude limit
        self.plot_widget.setLabel('left', 'Magnitude', units='dB')
        self.plot_widget.setLabel('bottom', 'Frequency', units='Hz')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Initialize a solid green curve line for the EQ plot
        self.curve = self.plot_widget.plot(pen=pg.mkPen('g', width=2))
        
        # Compute frequency bin mappings for the X-axis
        self.frequencies = np.fft.rfftfreq(CHUNK, d=1.0/RATE)
        self.plot_widget.setXRange(0, 20000) # Cut off visual at human hearing limit (20kHz)
        
        # Initialize PyAudio
        self.p = pyaudio.PyAudio()
        
        # Automatically look for a loopback or monitor device index to grab internal system audio
        device_index = None 
        print("--- Scanning Audio Input Devices ---")
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            print(f"Device {i}: {dev['name']} (Channels: {dev['maxInputChannels']})")
            
            # Match common loopback/system audio keywords
            if any(k in dev['name'].lower() for k in ["loopback", "monitor", "output.monitor"]):
                device_index = i
                
        if device_index is not None:
            print(f"\n--> Selected Device Index {device_index} for system audio loopback capture.")
        else:
            print("\n--> No explicit loopback device detected. Using system default input device.")
            print("    (Note: You may need to create a loopback device or use PulseAudio/PipeWire volume control to route system audio.)")

        # Open the live audio loopback stream
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=CHUNK
        )
        
        # Setup a QTimer to poll audio data and refresh the visualizer screen loop
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(UPDATE_MS)

    def update_plot(self):
        try:
            # Read raw binary data from the audio stream loopback
            # exception_on_overflow=False prevents crashes if the Raspberry Pi experiences jitter
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            
            # Convert binary audio buffer into a NumPy 16-bit integer array
            signal = np.frombuffer(data, dtype=np.int16)
            
            # Apply a Hanning window to prevent edge spectral leakage artifacts
            windowed_signal = signal * np.hanning(len(signal))
            
            # Compute the Real Fast Fourier Transform (RFFT)
            fft_data = np.fft.rfft(windowed_signal)
            magnitude = np.abs(fft_data)
            
            # Convert amplitude magnitude to an approximate dB Log Scale (+1 prevents log(0) errors)
            log_magnitude = 20 * np.log10(magnitude + 1)
            
            # Update the PyQtGraph curve with the calculated EQ data
            self.curve.setData(self.frequencies, log_magnitude)
            
        except Exception as e:
            pass # Ignore dropped frame exceptions to keep execution smooth

    def closeEvent(self, event):
        # Gracefully terminate streams and clean up hardware resources upon closing
        self.timer.stop()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    visualizer = AudioEQVisualizer()
    visualizer.show()
    sys.exit(app.exec_())