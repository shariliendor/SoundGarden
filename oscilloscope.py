import tkinter as tk
from collections import deque

import matplotlib
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlantOscilloscope:
    def __init__(self, plant_names, num_plants=8, N=100):
        self.N = N
        self.num_plants = num_plants
        self.plant_names = plant_names

        self.plant_buffers = [
            deque([0] * self.N, maxlen=self.N)
            for _ in range(self.num_plants)
        ]

        self.start()

    """
    Creates and starts up the plot visualizer
    """
    def start(self):
        plt.style.use("dark_background")
        plt.rcParams["toolbar"] = "None"

        self.root = tk.Tk()
        self.root.title("Sound Garden")
        self.root.attributes("-fullscreen", True)

        self.root.bind("<Escape>",lambda event: self.root.attributes("-fullscreen", False))

        self.fig, self.ax = plt.subplots(figsize=(14, 8))

        self.lines = []

        # dark styling to make it look more oscilloscope-like
        self.ax.set_facecolor('#000000')
        self.fig.patch.set_facecolor("#1D1D1D")

        colors = ['#00FF00', '#00FFFF', '#FFFF00', '#FF00FF', '#FF5555', '#55FF55', '#5555FF', '#FFFFFF']
        linestyles = ['-', '--', '-.', ':']

        for i in range(self.num_plants):
            line, = self.ax.plot(
                range(self.N),
                list(self.plant_buffers[i]),
                color=colors[i % len(colors)],
                linestyle=linestyles[i % len(linestyles)],
                label=self.plant_names[i]
            )

            self.lines.append(line)

        # oscilloscope grid look
        self.ax.set_axisbelow(True)

        self.ax.grid(
            True,
            which='major',
            linestyle='-',
            linewidth=0.6,
            color='#444444'
        )

        self.ax.minorticks_on()

        self.ax.grid(
            True,
            which='minor',
            linestyle=':',
            linewidth=0.5,
            color='#333333'
        )

        # Labels and title
        self.ax.set_title(
            "Bioelectric Signal (Touch Sensor)",
            color='#AAAAAA'
        )

        # custom legend:
        self.ax.legend(
            loc='lower center',
            bbox_to_anchor=(0.5, 1.1),
            ncol=self.num_plants,
            fontsize=8,
            handlelength=1.2,
            handletextpad=0.3,
            columnspacing=0.8,
            frameon=False
        )

        self.fig.subplots_adjust(top=0.85)

        self.ax.set_ylim(0, 100000)

        self.ax.tick_params(
            labelbottom=False,
            labelleft=False
        )

        self.canvas = FigureCanvasTkAgg(
            self.fig,
            master=self.root
        )

        self.canvas.draw()

        self.canvas.get_tk_widget().pack(
            fill=tk.BOTH,
            expand=True
        )

    """
    Updates all plant lines in the plot
    values : an array of integers representing the updated plant reading values
    Note: the plants are identified by their index position in array
    """
    def update_plot(self, values):
        for i, val in enumerate(values):
            self.plant_buffers[i].append(val)

            self.lines[i].set_ydata(self.plant_buffers[i])

            self.lines[i].set_xdata(
                range(len(self.plant_buffers[i]))
            )

        self.canvas.draw_idle()

        self.root.update_idletasks()
        self.root.update()

