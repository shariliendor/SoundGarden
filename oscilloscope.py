import matplotlib.pyplot as plt
from collections import deque

class PlantOscilloscope:
    def __init__(self, plant_names, num_plants=8, N=100):
        self.N = N
        self.num_plants = num_plants
        self.plant_names = plant_names
        self.is_running = True

        self.plant_buffers = [
            deque([0] * self.N, maxlen=self.N)
            for i in range(self.num_plants)
        ]

        self.start()

    def start(self):
        self.plt = plt
        self.plt.ion()
        self.plt.rcParams['toolbar'] = 'None'

        # Large text for CRT readability
        self.plt.rcParams.update({
            'font.size': 18,
            'axes.titlesize': 28,
            'axes.labelsize': 20,
            'xtick.labelsize': 18,
            'ytick.labelsize': 18,
            'legend.fontsize': 16,
            'figure.autolayout': False,
        })

        # Dark oscilloscope appearance
        self.plt.style.use('dark_background')

        # Create figure
        self.fig, self.ax = self.plt.subplots(figsize=(12, 7))

        # Fullscreen
        try:
            self.plt.get_current_fig_manager().full_screen_toggle()
        except Exception:
            pass

        # Keyboard and close events
        self.fig.canvas.mpl_connect(
            'key_press_event', self.on_key_press
        )
        self.fig.canvas.mpl_connect(
            'close_event', self.on_close
        )

        self.lines = []

        self.ax.set_facecolor('#000000')
        self.fig.patch.set_facecolor('#1D1D1D')

        colors = [
            '#00FF00',  # Green
            '#00FFFF',  # Cyan
            '#FFFF00',  # Yellow
            '#FF00FF',  # Magenta
            '#FF5555',  # Red
            '#55FF55',  # Light green
            '#5555FF',  # Blue
            '#FFFFFF',  # White
        ]

        linestyles = ['-', '--', '-.', ':']

        # Create thick signal lines
        for i in range(self.num_plants):
            line, = self.ax.plot(
                list(self.plant_buffers[i]),
                color=colors[i % len(colors)],
                linestyle=linestyles[i % len(linestyles)],
                linewidth=3.5,
                label=self.plant_names[i]
            )
            self.lines.append(line)

        # Grid
        self.ax.set_axisbelow(True)

        self.ax.grid(
            True,
            which='major',
            linestyle='-',
            linewidth=1.0,
            color='#444444'
        )

        self.ax.minorticks_on()

        self.ax.grid(
            True,
            which='minor',
            linestyle=':',
            linewidth=0.8,
            color='#333333'
        )

        # Plot border
        for spine in self.ax.spines.values():
            spine.set_color('#666666')
            spine.set_linewidth(1.2)

        # Title
        self.ax.set_title(
            'Bioelectric Signal (Touch Sensor)',
            color='#AAAAAA',
            fontsize=28,
            pad=20
        )

        # All plant names on one line
        self.ax.legend(
            loc='lower center',
            bbox_to_anchor=(0.5, 1.14),
            ncol=self.num_plants,
            fontsize=16,
            handlelength=1.3,
            handletextpad=0.4,
            columnspacing=0.8,
            labelspacing=0.8,
            frameon=False,
            borderaxespad=0
        )

        # Keep the plot away from the screen edges
        # Reduce the top margin to move the legend nearer the top
        self.fig.subplots_adjust(
            top=0.79,
            bottom=0.08,
            left=0.04,
            right=0.96
        )

        # Signal range
        self.ax.set_ylim(0, 5000)
        self.ax.set_xlim(0, self.N - 1)

        # Hide axis ticks and numbers
        self.ax.tick_params(
            which='both',
            bottom=False,
            top=False,
            left=False,
            right=False,
            labelbottom=False,
            labelleft=False
        )

        # Show the window
        self.plt.show(block=False)
        self.plt.pause(0.1)

    def on_key_press(self, event):
        # Press q or Escape to quit
        if event.key in ['q', 'escape']:
            self.is_running = False
            self.plt.close(self.fig)

    def on_close(self, event):
        self.is_running = False

    def update_plot(self, values):
        # Stop updating if the window has closed
        if not self.plt.fignum_exists(self.fig.number):
            self.is_running = False
            return

        # Update plant signals
        for i, val in enumerate(values):
            self.plant_buffers[i].append(val)
            self.lines[i].set_ydata(
                list(self.plant_buffers[i])
            )

        try:
            self.fig.canvas.draw_idle()
            self.plt.pause(0.001)

        except Exception as exc:
            print(f'Oscilloscope update failed: {exc}')
            self.is_running = False