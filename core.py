import numpy as np
import math

color_options = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
color_index = 0


# -------------------------------------
#                                     |
#       Drawing Functions             |
#                                     |
# -------------------------------------

def add_point(x_location, global_axes):
    if global_axes is None:
        raise RuntimeError("Graph has not been created yet.")
    global_axes.plot([x_location], [0], marker="o", linestyle="")
    global_axes.axvline(x=x_location, color="red", linestyle="-")

def add_lorentz_curves(global_axes, intervals=None):
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

        alpha = 0.2

        global_axes.plot(x_vals, y, color=color_options[color_index], linestyle="-", label=label, alpha=alpha)
        global_axes.plot(x_vals, -y, color=color_options[color_index], linestyle="-", alpha=alpha)

        global_axes.plot(x_branch, y_vals, color=color_options[color_index], linestyle="-", label=label, alpha=alpha)
        global_axes.plot(-x_branch, y_vals, color=color_options[color_index], linestyle="-", alpha=alpha)

        if (color_index < 6):
            color_index += 1
        else:
            color_index = 0

def calculate_frame(x_intercept, β, global_axes):
    if (β >= 1 or β <= -1):
        raise ValueError(f"β cannot be greater than, less than, or equal to speed of light")
    
    x = (np.linspace(-β - 100, β + 100, 1000))

    slope = (1 / β)

    equation_t = (slope * x) - (x_intercept / β)
    equation_x = (β * x) - (x_intercept * β)

    global_axes.plot(x, equation_t, color="blue")
    global_axes.plot(x, equation_x, color="orange")
