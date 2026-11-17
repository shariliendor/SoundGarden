import time
import numpy as np
import matplotlib.pyplot as plt


class PlantOscilloscope:

    def __init__(self, plant_names, num_plants=6, N=100):

        self.N = N
        self.num_plants = num_plants
        self.plant_names = plant_names
        self.is_running = True

        # Store signal history using NumPy arrays
        self.plant_buffers = [
            np.zeros(self.N)
            for _ in range(self.num_plants)
        ]

        # FPS monitoring
        self.frame_count = 0
        self.fps_start = time.time()

        self.background = None
        self.use_blitting = False

        self.start()

    def start(self):

        self.plt = plt

        self.plt.ion()
        self.plt.rcParams['toolbar'] = 'None'

        # CRT readability
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
        self.fig, self.ax = self.plt.subplots(
            figsize=(12, 7)
        )

        # Fullscreen
        try:
            self.plt.get_current_fig_manager().full_screen_toggle()
        except Exception:
            pass

        # Keyboard and close events
        self.fig.canvas.mpl_connect(
            'key_press_event',
            self.on_key_press
        )

        self.fig.canvas.mpl_connect(
            'close_event',
            self.on_close
        )

        self.lines = []

        self.ax.set_facecolor('#000000')
        self.fig.patch.set_facecolor('#1D1D1D')

        colors = [
            '#ff0056', # Pothos = ?
            "#ff8000", # Alocasia = ?
            '#ffe400', # African Violet = ?
            "#f200ff", # Philodendron = purple
            '#00bd9e', # Peperomia = green
            '#0053fe', # Monstera = blue?
        ]

        linestyles = ['-', '--', '-.', ':']

        # Create signal lines
        for i in range(self.num_plants):

            line, = self.ax.plot(
                self.plant_buffers[i],
                color=colors[i % len(colors)],
                linestyle=linestyles[i % len(linestyles)],
                linewidth=1.8,
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

        # Disable minor gridlines
        self.ax.minorticks_off()

        # Plot border
        for spine in self.ax.spines.values():
            spine.set_color('#666666')
            spine.set_linewidth(1.2)

        # Title
        self.ax.set_title(
            'Bioelectric Signal',
            color='#AAAAAA',
            fontsize=28,
            pad=20
        )

        # Legend
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

        # Figure margins
        self.fig.subplots_adjust(
            top=0.79,
            bottom=0.08,
            left=0.04,
            right=0.96
        )

        # Signal range
        self.ax.set_ylim(0, 5000)
        self.ax.set_xlim(0, self.N - 1)

        # Hide axis ticks
        self.ax.tick_params(
            which='both',
            bottom=False,
            top=False,
            left=False,
            right=False,
            labelbottom=False,
            labelleft=False
        )

        # Show window
        self.plt.show(block=False)
        self.plt.pause(0.1)

        # Enable blitting if supported
        self.use_blitting = self.fig.canvas.supports_blit

        if self.use_blitting:

            # Draw static background
            self.fig.canvas.draw()

            self.background = (
                self.fig.canvas.copy_from_bbox(
                    self.ax.bbox
                )
            )

            # Mark signal lines as animated
            for line in self.lines:
                line.set_animated(True)

        print("Oscilloscope initialized")
        print("Blitting enabled:", self.use_blitting)

    def on_key_press(self, event):

        if event.key in ['q', 'escape']:

            self.is_running = False
            self.plt.close(self.fig)

    def on_close(self, event):

        self.is_running = False

    def update_plot(self, values):

        # Stop updating if window is closed
        if not self.plt.fignum_exists(self.fig.number):

            self.is_running = False
            return

        # Update signal buffers
        for i, val in enumerate(values):

            self.plant_buffers[i] = np.roll(
                self.plant_buffers[i],
                -1
            )

            self.plant_buffers[i][-1] = val

            self.lines[i].set_ydata(
                self.plant_buffers[i]
            )

        try:

            if self.use_blitting:

                # Restore static background
                self.fig.canvas.restore_region(
                    self.background
                )

                # Redraw only signal lines
                for line in self.lines:

                    self.ax.draw_artist(line)

                # Update graph area
                self.fig.canvas.blit(
                    self.ax.bbox
                )

                self.fig.canvas.flush_events()

            else:

                # Fallback rendering
                self.fig.canvas.draw_idle()
                self.plt.pause(0.001)

        except Exception as exc:

            print(
                f'Oscilloscope update failed: {exc}'
            )

            self.is_running = False
            return

        # FPS monitoring
        self.frame_count += 1

        elapsed = time.time() - self.fps_start

        if elapsed >= 2:

            fps = self.frame_count / elapsed

            print(f"Graph FPS: {fps:.1f}")

            self.frame_count = 0
            self.fps_start = time.time()
