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

step = 24 / divisions # space between each tick

tick_origin_x = None
tick_origin_y = None

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
    core.add_point(x, global_axes)
    canvas.draw_idle()

def submit_event_a(x, y, canvas):
    try:
        float(x)
    except ValueError:
        raise ValueError(f"Cannot convert '{x}' to a float.")
    
    try:
        float(y)
    except ValueError:
        raise ValueError(f"Cannot convert '{y}' to a float.")
    
    
    x = float(x)
    y = float(y)
    core.add_event_a(x, y, global_axes, canvas)
    canvas.draw_idle()

def submit_event_b(x, y, canvas):
    try:
        float(x)
    except ValueError:
        raise ValueError(f"Cannot convert '{x}' to a float.")
    
    try:
        float(y)
    except ValueError:
        raise ValueError(f"Cannot convert '{y}' to a float.")
    
    
    x = float(x)
    y = float(y)
    core.add_event_b(x, y, global_axes, canvas)
    canvas.draw_idle()
    

def submit_function_2(x, y, canvas):
    try:
        float(x)
    except ValueError:
        raise ValueError(f"Cannot convert '{x}' to a float.")
    try:
        float(y)
    except ValueError:
        raise ValueError(f"Cannot convert '{y}' to a float.")
    
    x_intercept = float(x)
    β = float(y) # this is awesome that python lets us use symbols
    
    #do something here
    core.calculate_frame(x_intercept, β, global_axes)

    

    canvas.draw_idle()

    global_axes.legend(bbox_to_anchor=(1, 1), loc='upper left', borderaxespad=0.)
    plt.show()
    

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
        
    picked_point = None
    annotation = None

    def button_release_event(event):
        nonlocal picked_point, annotation
        state["event"] = None
        if picked_point is not None:
            picked_point.remove()
            picked_point = None
            axes.figure.canvas.draw_idle()

        if annotation is not None:
            annotation.remove()
            annotation = None
            axes.figure.canvas.draw_idle()
    
    def onpick(event):
        global step
        nonlocal picked_point, annotation

        line = core.get_tprime()
        x_line = core.get_xprime()

        line_other = core.get_t()
        x_line_other = core.get_x()
        β = core.get_β()

        if event.artist == line or event.artist == line_other:
            the_line = None
            text = None
            text_x = None
            if event.artist == line:
                the_line = line
                text = "t\'"
                text_x = "x\'"
            elif event.artist == line_other:
                the_line = line_other
                text = "t"
                text_x = "x"
            # index of the picked point
            ind = event.ind[0]

            x_val = the_line.get_xdata()[ind]
            y_val = the_line.get_ydata()[ind]
            #print(f"Picked point: index={ind}, x={x_val:.2f}, y={y_val:.2f}")

            if picked_point is not None:
                picked_point.remove()

            # create a point for the thing
            picked_point, = axes.plot([x_val], [y_val], marker='o', markersize=8, color='red')

            if annotation is not None:
                annotation.remove()

            if text == "t\'":
                # add text for the point
                annotation = global_axes.annotate(
                    f'Point: ({text} = {core.calculate_t_prime(y_val, x_val, β)}, {text_x} = {core.calculate_x_prime(y_val, x_val, β)})',  # Annotation text
                    xy=(x_val, y_val),            # Point to annotate
                    xytext=(x_val + step * 0.25, y_val + step * 0.5), # Text position (offset from xy)
                    arrowprops=dict(facecolor='black', shrink=step * 0.1), # Arrow properties
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1, alpha=0.9), # Text box properties
                    ha='left', va='bottom' # Horizontal and vertical alignment of text
                )
            if text == "t":
                annotation = global_axes.annotate(
                    f'Point: ({text} = {core.calculate_t(y_val, x_val, β)}, {text_x} = {core.calculate_x(y_val, x_val, β)})',  # Annotation text
                    xy=(x_val, y_val),            # Point to annotate
                    xytext=(x_val + step * 0.25, y_val + step * 0.5), # Text position (offset from xy)
                    arrowprops=dict(facecolor='black', shrink=step * 0.1), # Arrow properties
                    bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1, alpha=0.9), # Text box properties
                    ha='left', va='bottom' # Horizontal and vertical alignment of text
                )

            axes.figure.canvas.draw_idle()
        if event.artist == x_line or event.artist == x_line_other:
            the_line = None
            text = None
            text_x = None
            if event.artist == x_line:
                the_line = x_line
                text = "t\'"
                text_x = "x\'"
            elif event.artist == x_line_other:
                the_line = x_line_other
                text = "t"
                text_x = "x"

            # index of the picked point
            ind = event.ind[0]

            x_val = the_line.get_xdata()[ind]
            y_val = the_line.get_ydata()[ind]
            print(f"Picked point: index={ind}, x={x_val:.2f}, y={y_val:.2f}")

            if picked_point is not None:
                picked_point.remove()

            # create a point for the thing
            picked_point, = axes.plot([x_val], [y_val], marker='o', markersize=8, color='red')

            if annotation is not None:
                annotation.remove()

            # add text for the point
            annotation = global_axes.annotate(
                f'Point: ({text} = {core.calculate_t_prime(y_val, x_val, β)}, {text_x} = {core.calculate_x_prime(y_val, x_val, β)})',  # Annotation text
                xy=(x_val, y_val),            # Point to annotate
                xytext=(x_val + step * 0.25, y_val + step * 0.5), # Text position (offset from xy)
                arrowprops=dict(facecolor='black', shrink=step * 0.1), # Arrow properties
                bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1, alpha=0.9), # Text box properties
                ha='left', va='bottom' # Horizontal and vertical alignment of text
            )

            axes.figure.canvas.draw_idle()

    axes.figure.canvas.mpl_connect('pick_event', onpick)

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
    
    # Add x-axis line at y=0
    global_axes.axhline(0, color='black', linewidth=0.8, linestyle='--')

    # Add y-axis line at x=0
    global_axes.axvline(0, color='black', linewidth=0.8, linestyle='--')
    
    global_axes.grid(True)

    ticks = _build_ticks([-x_lim - 1, x_lim + 1], [-y_lim - 1, y_lim + 1])
    global_axes.set_xticks(ticks[0])
    global_axes.set_yticks(ticks[1])

    global_axes.set_xlim(-x_lim, x_lim)
    global_axes.set_ylim(-y_lim, y_lim)

    core.add_lorentz_curves(global_axes)

    global_axes.legend(bbox_to_anchor=(1, 1), loc='upper left', borderaxespad=0.)
    return global_figure
    

# -------------------------------------
#                                     |
#                main                 |
#                                     |
# -------------------------------------

def main():
    # This is where we do all of our tkinter stuff
    window = tk.Tk()
    window.title("Spacetime Diagram")
    window.geometry("1080x1080")

    greeting = tk.Label(window, text="Stationary object's location")
    greeting.place(x=10, y=10)

    input = tk.Entry(window, text="Enter here: ", bg="white", fg="black")
    input.place(x=10, y=30)

    submit_button = tk.Button(window, text="Submit", command=lambda: submit_function(input.get(), canvas))
    submit_button.place(x=10, y=60)  

    remove_button = tk.Button(window, text="Remove", command=lambda: core.remove_function(canvas))
    remove_button.place(x=100, y=60)  

    # -----------------------------------------------------------------------------------------------------    

    # repeated code
    greeting_2 = tk.Label(window, text="Add a inertial frame. (top input is x' at t'=0, bottom input is β)")
    greeting_2.place(x=250, y=10)

    input_2_1 = tk.Entry(window, text="Enter here: 2", bg="white", fg="black")
    input_2_1.place(x=250, y=30)
    input_2_2 = tk.Entry(window, text="Enter here: 3", bg="white", fg="black")
    input_2_2.place(x=250, y=60)

    submit_button_2 = tk.Button(window, text="Submit", command=lambda: submit_function_2(input_2_1.get(), input_2_2.get(), canvas))
    submit_button_2.place(x=450, y=30) 

    remove_button_2 = tk.Button(window, text="Remove", command=lambda: core.remove_frame(canvas))
    remove_button_2.place(x=450, y=60) 

    transform_button = tk.Button(window, text="Transform!", command=lambda: core.transform_view(canvas, global_axes))
    transform_button.place(x=540, y=60)

    #input_worldline = create_input_box(window, "Worldine", "white", "black") 

    # closes the window
    quit_button = tk.Button(window, text="Quit", command=lambda: stop(window))
    quit_button.place(x=517, y=1020)

    # -----------------------------------------------------------------------------------------------------    
    # Event A

    greeting_3 = tk.Label(window, text="Add event A (t, x): ")
    greeting_3.place(x=650, y=10)
    input_3_x = tk.Entry(window, text="Enter here: 4", bg="white", fg="black", width=5)
    input_3_x.place(x=650, y=30)

    input_3_y = tk.Entry(window, text="Enter here: 6", bg="white", fg="black", width=5)
    input_3_y.place(x=710, y=30)

    submit_button_3 = tk.Button(window, text="Submit", command=lambda: submit_event_a(input_3_y.get(), input_3_x.get(), canvas))
    submit_button_3.place(x=650, y=60)  

    remove_button_3 = tk.Button(window, text="Remove", command=lambda: core.remove_a(canvas))
    remove_button_3.place(x=750, y=60)  
    
    # -----------------------------------------------------------------------------------------------------    

    greeting_4 = tk.Label(window, text="Add event B")
    greeting_4.place(x=850, y=10)
    input_4 = tk.Entry(window, text="Enter here: 5", bg="white", fg="black", width=5)
    input_4.place(x=850, y=30)

    input_4_y = tk.Entry(window, text="Enter here: 7", bg="white", fg="black", width=5)
    input_4_y.place(x=910, y=30)

    submit_button_4 = tk.Button(window, text="Submit", command=lambda: submit_event_b(input_4_y.get(), input_4.get(), canvas))
    submit_button_4.place(x=850, y=60)  

    remove_button_4 = tk.Button(window, text="Remove", command=lambda: core.remove_b(canvas))
    remove_button_4.place(x=950, y=60)  


    # -----------------------------------------------------------------------------------------------------    

    # Here we make the actual matplotlib graph
    figure = create_graph()
    canvas = FigureCanvasTkAgg(figure, master=window)
    canvas.draw_idle() # draw it
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=70, pady=100)

    # bind global_axes events to these ones we are defining in these functions
    zoom_factory(global_axes)
    move_factory(global_axes)

    # main event loop
    window.mainloop()
