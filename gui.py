import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import numpy as np

import matplotlib.pyplot as plt
import math

import core

# -------------------------------------
#                                     |
#              Globals                |
#                                     |
# -------------------------------------

global_figure = None  # canvas
global_axes = None  # single plot area inside figure

x_lim = 10 # default
y_lim = 10 # default
divisions = 12 # default, how many ticks there are

color_options = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
color_index = 0

step = 24 / divisions # space between each tick

tick_origin_x = None
tick_origin_y = None

lorentz_curves = []

# -------------------------------------
#                                     |
#       Tkinter Functions             |
#                                     |
# -------------------------------------

def submit_function(x, canvas):
    try:
        float(x)
    except ValueError:
        raise ValueError(f"Cannot convert '{x}' to a float.")
    
    x = float(x)
    add_point(x)
    canvas.draw_idle()

def stop(window):
    window.destroy() 
    global global_figure, global_axes
    if global_figure is not None:
        plt.close(global_figure)
    global_figure = None
    global_axes = None


# -------------------------------------
#                                     |
#       Ticks Functions.              |
#                                     |
# -------------------------------------

def _build_ticks(limx, limy):
    global step, tick_origin_x, tick_origin_y, divisions
    spanx = limx[1] - limx[0]
    step = spanx / divisions

    # have to update origin after zooming out
    tick_origin_x = limx[0]
    tick_origin_y = limy[0]

    return [np.arange(limx[0], limx[1], step), np.arange(limy[0], limy[1], step)]

def _build_ticks_move(limx, limy):
    global step, tick_origin_x, tick_origin_y

    if step <= 0:
        raise RuntimeError("step must be computed before calling _build_ticks_move")
    if tick_origin_x is None or tick_origin_y is None:
        raise RuntimeError("tick origins must be set before calling _build_ticks_move")

    def _ticks_for_limits(limits, origin):
        start = limits[0] # first element
        end = limits[1] # second element (end)

        offset_steps = math.floor((start - origin) / step) # number of steps needed to get in view

        first_tick = origin + offset_steps * step # actual first viewable tick location


        # np.arrange stops before the upper bound, so we push the bound a little past end (end + 0.5 * step)
        # to guarantee inclusion of a tick lying exactly at end.
        ticks = np.arange(first_tick, end + step * 0.5, step)

        
        # a very small number we add on to start or end in order to prevent floating-point tiny errors
        # ex. 7.00001, wouldn't be included in end = 7 or something. So we add 7 + (step * 0.05) = 7.1
        eps = step * 0.05 

        # ^ this could be not neccessary at all

        visible = ticks[(ticks >= start) & (ticks <= end)] # previously start - eps, end + eps

        return visible

    return [_ticks_for_limits(limx, tick_origin_x), _ticks_for_limits(limy, tick_origin_y)]


# -------------------------------------
#                                     |
#       Pan / Zoom                    |
#                                     |
# -------------------------------------

# Working perfectly
def zoom_factory(axes, base_scale=1.2):
    def zoom(event):
        current_xlim = axes.get_xlim()
        span = current_xlim[1] - current_xlim[0]
        new_width = span * (1 / base_scale if event.button == "up" else base_scale)

        # keep origin centered
        half = new_width / 2
        axes.set_xlim(-half, half)

        current_ylim = axes.get_ylim()
        height = current_ylim[1] - current_ylim[0]
        new_height = height * (1 / base_scale if event.button == "up" else base_scale)
        axes.set_ylim(-new_height / 2, new_height / 2)

        # and also set the ticks,
        new_x_lim = axes.get_xlim()
        new_y_lim = axes.get_ylim()

        x_ticks, y_ticks = _build_ticks(new_x_lim, new_y_lim)
        axes.set_xticks(x_ticks)
        axes.set_yticks(y_ticks)

        # In the future we should be updating curves based on view
        # add_lorentz_curves()

        axes.figure.canvas.draw_idle()

    # stores callback function, zoom, for scroll event
    return axes.figure.canvas.mpl_connect("scroll_event", zoom)


# Not working perfectly
def move_factory(axes):
    state = {"event": None}

    def button_press_event(event):
        if (event.inaxes != axes):
            return
        
        if (event.button == 1):    
            current_xlim = axes.get_xlim()
            current_ylim = axes.get_ylim()
            xdata = event.xdata
            ydata = event.ydata

            state["event"] = {
                "x": xdata,
                "y": ydata,
                "xlim": current_xlim,
                "ylim": current_ylim
            }
        
    def motion_notify_event(event):
        if (event.inaxes != axes or state["event"] == None or event.xdata == None or event.ydata == None):
            return
        
        current_xlim = state["event"]["xlim"]
        current_ylim = state["event"]["ylim"]
        xdata = state["event"]["x"]
        ydata = state["event"]["y"]
        
        # I should change this because it is horrible to read
        dx = xdata - event.xdata
        dy = ydata - event.ydata

        # there is something buggy with this code, it keeps snapping
        axes.set_xlim([current_xlim[0] + dx, current_xlim[1] + dx])
        axes.set_ylim([current_ylim[0] + dy, current_ylim[1] + dy])

        state["event"]["xlim"] = axes.get_xlim()
        state["event"]["ylim"] = axes.get_ylim()

        # and also set the ticks, this needs a lot of work
        new_x_lim = axes.get_xlim()
        new_y_lim = axes.get_ylim()

        x_ticks, y_ticks = _build_ticks_move(new_x_lim, new_y_lim)
        axes.set_xticks(x_ticks)
        axes.set_yticks(y_ticks)


        # In the future we should be updating curves based on view
        #add_lorentz_curves()

        axes.figure.canvas.draw_idle()
        

    def button_release_event(event):
        state["event"] = None

    axes.figure.canvas.mpl_connect("button_press_event", button_press_event)
    axes.figure.canvas.mpl_connect("motion_notify_event", motion_notify_event)
    axes.figure.canvas.mpl_connect("button_release_event", button_release_event)
    
    
# -------------------------------------
#                                     |
#       Initial Graph.                |
#                                     |
# -------------------------------------

def create_graph():
    global global_figure, global_axes
    global_figure = Figure(figsize=(10, 8), dpi=100)
    global_axes = global_figure.add_subplot(111)
    
    global_axes.grid(True)

    ticks = _build_ticks([-x_lim - 1, x_lim + 1], [-y_lim - 1, y_lim + 1])
    global_axes.set_xticks(ticks[0])
    global_axes.set_yticks(ticks[1])

    global_axes.set_xlim(-x_lim, x_lim)
    global_axes.set_ylim(-y_lim, y_lim)

    add_lorentz_curves()
    return global_figure
    

# -------------------------------------
#                                     |
#       Drawing Functions             |
#                                     |
# -------------------------------------

def add_point(x_location: float):
    if global_axes is None:
        raise RuntimeError("Graph has not been created yet.")
    global_axes.plot([x_location], [0], marker="o", linestyle="")
    global_axes.axvline(x=x_location, color="red", linestyle="-")

def add_worldline(x_intercept, velocity):
    core.create_worldline(x_intercept, velocity, global_axes)


def add_lorentz_curves(intervals=None):
    global color_index, color_options
    if global_axes is None:
        raise RuntimeError("Graph has not been created yet.")

    if intervals is None:
        #intervals = list(range(1, y_lim + 1))
        intervals = list(range(1, 100))

    #x_vals = np.linspace(-x_lim, x_lim, 200)
    #y_vals = np.linspace(-y_lim, y_lim, 200)

    # Bruteforce 1000 seconds
    x_vals = np.linspace(-100, 100, 4000)
    y_vals = np.linspace(-100, 100, 4000)

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


# -------------------------------------
#                                     |
#                main                 |
#                                     |
# -------------------------------------

def create_input_box(window, text, bg, fg):
    greeting = tk.Label(window, text=text)
    greeting.pack()

    input = tk.Entry(window, text="Enter here: ", bg="white", fg="black")
    input.pack()
    return input


def main():
    # This is where we do all of our tkinter stuff
    window = tk.Tk()
    window.title("Spacetime Diagram")
    window.geometry("1000x1000")

    input_object = create_input_box(window, "Object's x location", "white", "black")

    submit_button = tk.Button(window, text="Submit", command=lambda: submit_function(input.get(), canvas))
    submit_button.pack()   

    #input_worldline = create_input_box(window, "Worldine", "white", "black") 

    # closes the window
    quit_button = tk.Button(window, text="Quit", command=lambda: stop(window))
    quit_button.pack()

    # -----------------------------------------------------------------------------------------------------    

    # Here we make the actual matplotlib graph
    figure = create_graph()
    canvas = FigureCanvasTkAgg(figure, master=window)
    canvas.draw_idle() # draw it
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10) # what does this do?

    # bind global_axes events to these ones we are defining in these functions
    zoom_factory(global_axes)
    move_factory(global_axes)

    # main event loop
    window.mainloop()
