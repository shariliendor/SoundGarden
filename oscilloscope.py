import matplotlib.pyplot as plt
from collections import deque

class PlantOscilloscope:
    def __init__(self, plant_names, num_plants=8, N=100):
        self.N = N
        self.num_plants = num_plants
        self.plant_names = plant_names

        self.plant_buffers = [deque([0]*self.N, maxlen=self.N) for i in range(self.num_plants)]
        self.start() # start the plot graph

    """
    Creates and starts up the plot visualizer
    """
    def start(self):
        self.plt = plt
        self.plt.ion()
        plt.rcParams['toolbar'] = 'None' # get rid of the bottom toolbar

        self.fig, self.ax = self.plt.subplots()
        self.plt.get_current_fig_manager().full_screen_toggle()
        # self.fig.subplots_adjust(left=0.15) # some padding for left-hand side
        self.lines = []

        # dark styling to make it look more oscilloscope-like
        self.plt.style.use('dark_background')
        self.ax.set_facecolor('#000000')
        self.fig.patch.set_facecolor("#1D1D1D")

        colors = ['#00FF00', '#00FFFF', '#FFFF00', '#FF00FF', '#FF5555', '#55FF55', '#5555FF', '#FFFFFF']
        linestyles = ['-', '--', '-.', ':']

        for i in range(self.num_plants):
            line, = self.ax.plot(
                self.plant_buffers[i],
                color=colors[i % len(colors)],
                linestyle=linestyles[i % len(linestyles)],
                label=self.plant_names[i])
            self.lines.append(line) 

        # oscilloscope grid look
        self.ax.set_axisbelow(True)
        self.ax.grid(True, which='major', linestyle='-', linewidth=0.6, color='#444444')
        self.ax.minorticks_on()
        self.ax.grid(True, which='minor', linestyle=':', linewidth=0.5, color='#333333')

        # Labels and title
        self.ax.set_title("Bioelectric Signal (Touch Sensor)", color='#AAAAAA')
        #self.ax.set_ylabel("Charge Time (Voltage Proxy)", color='#AAAAAA')
        #self.ax.set_xlabel("Time (samples)", color='#AAAAAA')

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
        self.ax.tick_params(labelbottom = False, labelleft = False) # get rid of the number labels

    """
    Updates all plant lines in the plot
    values : an array of integers representing the updated plant reading values
    Note: the plants are identified by their index position in array
    """
    def update_plot(self, values):
        for i, val in enumerate(values):
            self.plant_buffers[i].append(val)
            self.lines[i].set_ydata(self.plant_buffers[i])
            self.lines[i].set_xdata(range(len(self.plant_buffers[i])))
        self.plt.pause(0.01)
