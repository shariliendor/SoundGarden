import matplotlib.pyplot as plt
from collections import deque

class PlantOscilloscope:
    def __init__(self, plant_names, num_plants=8, N=100):
        self.N = N
        self.num_plants = num_plants
        self.plant_names = plant_names
        self.is_running = True  # flag to safely stop the loop

        self.plant_buffers = [deque([0]*self.N, maxlen=self.N) for i in range(self.num_plants)]
        self.start() # start the plot graph

    def start(self):
        self.plt = plt
        self.plt.ion()
        self.plt.rcParams['toolbar'] = 'None' # get rid of the bottom toolbar

        # Apply dark background before creating the figure
        self.plt.style.use('dark_background')
        self.fig, self.ax = self.plt.subplots()

        # commented out for testing 
        # self.plt.get_current_fig_manager().full_screen_toggle()
        
        # Bind keyboard and window close events
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('close_event', self.on_close)

        self.lines = []

        # dark styling to make it look more oscilloscope-like
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

        for spine in self.ax.spines.values():
            spine.set_color('#444444')
            spine.set_linewidth(0.6)

        # Labels and title
        self.ax.set_title("Bioelectric Signal (Touch Sensor)", color='#AAAAAA')

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
        
        self.ax.set_ylim(0, 5000)
        self.ax.set_xlim(0, self.N - 1)
        
        self.ax.tick_params(
            which='both',
            bottom=False,
            top=False,
            left=False,
            right=False,
            labelbottom=False,
            labelleft=False
        )

    def on_key_press(self, event):
        # quit if user presses q or 'esc
        if event.key in ['q', 'escape']:
            self.is_running = False
            self.plt.close(self.fig)

    def on_close(self, event):
        self.is_running = False

    def update_plot(self, values):
        # check that the window wasn't closed before trying to update
        if not self.plt.fignum_exists(self.fig.number):
            self.is_running = False
            return

        for i, val in enumerate(values):
            self.plant_buffers[i].append(val)
            self.lines[i].set_ydata(self.plant_buffers[i])
            #self.lines[i].set_xdata(range(len(self.plant_buffers[i])))
            
        try:
            #self.plt.pause(0.01)
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()
        except Exception:
            self.is_running = False
