import matplotlib as mpl
mpl.rcParams['toolbar'] = 'None'
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt


global_figure = None  # canvas
global_axes = None  # single plot area inside figure

x_lim = 10 # default
y_lim = 10 # default

color_options = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
color_index = 0

def add_lorentz_curves(intervals=None):
    global color_index, color_options
    if global_axes is None:
        raise RuntimeError("Graph has not been created yet.")

    if intervals is None:
        intervals = list(range(1, y_lim + 1))


    # these may be using the incorrect variables
    x_vals = np.linspace(-x_lim, x_lim, 800)
    y_vals = np.linspace(-y_lim, y_lim, 800)

    for index, w_value in enumerate(intervals):
        if w_value <= 0:
            raise ValueError("Interval constants must be positive.")
        
        y = np.sqrt(x_vals ** 2 + w_value ** 2)
        x_branch = np.sqrt(y_vals ** 2 + w_value ** 2)

        if index == 0:
            label = "spacetime interval" 
        else: 
            None

        global_axes.plot(x_vals, y, color=color_options[color_index], linestyle="-", label=label, alpha=0.35)
        global_axes.plot(x_vals, -y, color=color_options[color_index], linestyle="-", alpha=0.35)

        global_axes.plot(x_branch, y_vals, color=color_options[color_index], linestyle="-", label=label, alpha=0.35)
        global_axes.plot(-x_branch, y_vals, color=color_options[color_index], linestyle="-", alpha=0.35)

        if (color_index < 6):
            color_index += 1
        else:
            color_index = 0


def create_graph():
    global global_figure, global_axes
    global_figure = Figure(figsize=(10, 8), dpi=100)
    global_axes = global_figure.add_subplot(111)
    
    global_axes.grid(True)
    global_axes.set_xticks(list(range(-x_lim - 1, x_lim + 1)))
    global_axes.set_yticks(list(range(-y_lim - 1, y_lim + 1)))


    global_axes.set_xlim(-x_lim, x_lim)
    global_axes.set_ylim(-y_lim, y_lim)

    add_lorentz_curves()
    return global_figure
    


def add_point(x_location: float):
    if global_axes is None:
        raise RuntimeError("Graph has not been created yet.")
    global_axes.plot([x_location], [0], marker="o", linestyle="")
    global_axes.axvline(x=x_location, color="red", linestyle="-")


def stop():
    global global_figure, global_axes
    if global_figure is not None:
        plt.close(global_figure)
    global_figure = None
    global_axes = None


def zoom_factory(axes, base_scale=1.2):
    def zoom(event):
        if event.inaxes != axes:
            # the event isn't in the main axes
            return
        current_xlim = axes.get_xlim()
        current_ylim = axes.get_ylim()
        xdata = event.xdata
        ydata = event.ydata
        
        # not sure what below does
        if event.button == "up":
            scale_factor = 1 / base_scale
        elif event.button == "down":
            scale_factor = base_scale
        else:
            return
        
        new_width = (current_xlim[1] - current_xlim[0]) * scale_factor
        new_height = (current_ylim[1] - current_ylim[0]) * scale_factor
        
        # numerator: distance from right, demoniator: full width
        x_edge_factor = (current_xlim[1] - xdata) / (current_xlim[1] - current_xlim[0])
        y_edge_factor = (current_ylim[1] - ydata) / (current_ylim[1] - current_ylim[0])

        # subtract from minimum, add to maximum for new width
        axes.set_xlim([xdata - new_width * (1 - x_edge_factor), xdata + new_width * x_edge_factor])
        axes.set_ylim([ydata - new_height * (1 - y_edge_factor), ydata + new_height * y_edge_factor])

        axes.figure.canvas.draw_idle()

    # stores callback function, zoom, for scroll event
    return axes.figure.canvas.mpl_connect("scroll_event", zoom)
    