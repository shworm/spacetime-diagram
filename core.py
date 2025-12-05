import numpy as np
import math

color_options = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
color_index = 0

t = None
x = None
tprime = None
xprime = None
x_new_frame = None
β = None
primary_view = "t"

point = None
point_line = None

event_a = None
a_annotation = None

event_b = None
b_annotation = None

def get_tprime():
    return tprime

def get_t():
    return t

def get_β():
    return β

def get_xprime():
    return xprime

def get_x():
    return x

# -------------------------------------
#                                     |
#       Drawing Functions             |
#                                     |
# -------------------------------------

def add_point(x_location, global_axes):
    global point, point_line
    if point is not None or point_line is not None:
        point.remove()
        point_line.remove()
        point = None
        point_line = None

    if global_axes is None:
        raise RuntimeError("Graph has not been created yet.")
    point, = global_axes.plot([x_location], [0], marker="o", linestyle="")
    point_line = global_axes.axvline(x=x_location, color="red", linestyle="-")

def add_event_a(x_location, y_location, global_axes, canvas):
    global event_a, a_annotation
    if event_a is not None:
        event_a.remove()
        event_a = None

    if a_annotation is not None:
        a_annotation.remove()
        a_annotation = None

    event_a, = global_axes.plot([x_location], [y_location], marker="o", linestyle="")

    a_annotation = global_axes.annotate(
        f'A: ({y_location}, {x_location})',
        xy=(x_location, y_location),            # Point to annotate
        xytext=(x_location + 2 * 0.25, y_location + 2 * 0.5), # Text position (offset from xy)
        arrowprops=dict(facecolor='black', shrink=2 * 0.1), # Arrow properties
        bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1, alpha=0.9), # Text box properties
        ha='left', va='bottom' # Horizontal and vertical alignment of text
    )

def add_event_b(x_location, y_location, global_axes, canvas):
    global event_b, b_annotation
    if event_b is not None:
        event_b.remove()
        event_b = None

    if b_annotation is not None:
        b_annotation.remove()
        b_annotation = None

    event_b, = global_axes.plot([x_location], [y_location], marker="o", linestyle="")

    b_annotation = global_axes.annotate(
        f'B: ({y_location}, {x_location})',
        xy=(x_location, y_location),            # Point to annotate
        xytext=(x_location + 2 * 0.25, y_location + 2 * 0.5), # Text position (offset from xy)
        arrowprops=dict(facecolor='black', shrink=2 * 0.1), # Arrow properties
        bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1, alpha=0.9), # Text box properties
        ha='left', va='bottom' # Horizontal and vertical alignment of text
    )

def transform_view(figure, global_axes):
    global tprime, xprime, β, event_a, event_b, x_new_frame, t, x, primary_view, a_annotation, b_annotation
    view = primary_view

    if (tprime == None and xprime == None and event_a == None and event_b == None):
        raise ValueError("We must have something to transform")
    
    if (tprime != None or xprime != None):
        if primary_view == "t":
            slope = (1 / β)

            x_vals = (np.linspace(-β - 50, β + 50, 4000))

            equation_t = -((slope * x_vals) - (x_new_frame / β))
            equation_x = -((β * x_vals) - (x_new_frame * β))

            tprime_line, = global_axes.plot(x_vals, equation_t, color="black", label="t'")
            xprime_line, = global_axes.plot(x_vals, equation_x, color="black", label="x'")

            # Enable pick events so gui.move_factory onpick sees these lines as artists
            #tprime_line.set_picker(5)
            #xprime_line.set_picker(5)
            t.remove()
            x.remove()

            t = tprime_line
            x = xprime_line

            t.set_picker(5)
            x.set_picker(5)

            tprime.remove()
            xprime.remove()

            tprime = global_axes.axvline(x=0, color='blue', linestyle="-", label='x')
            xprime = global_axes.axhline(y=0, color='orange', linestyle="-", label='t')
            primary_view = "tprime"
        else:
            slope = (1 / β)

            x_vals = (np.linspace(-β - 50, β + 50, 4000))

            equation_t = ((slope * x_vals) - (x_new_frame / β))
            equation_x = ((β * x_vals) - (x_new_frame * β))

            tprime_line, = global_axes.plot(x_vals, equation_t, color="blue", label="t'")
            xprime_line, = global_axes.plot(x_vals, equation_x, color="orange", label="x'")

            # Enable pick events so gui.move_factory onpick sees these lines as artists
            #tprime_line.set_picker(5)
            #xprime_line.set_picker(5)
            tprime.remove()
            xprime.remove()

            tprime = tprime_line
            xprime = xprime_line

            tprime.set_picker(5)
            xprime.set_picker(5)

            t.remove()
            x.remove()

            t = global_axes.axvline(x=0, color='black', linestyle="-", label='x')
            x = global_axes.axhline(y=0, color='black', linestyle="-", label='t')
            primary_view = "t"


    if (event_a != None and β != None):
        temp = event_a
        if (view == "t"):
            event_a, = global_axes.plot([calculate_x_prime(event_a.get_ydata(), event_a.get_xdata(), β)], [calculate_t_prime(event_a.get_ydata(), event_a.get_xdata(), β)], marker="o", linestyle="")
        elif (view == "tprime"):
            event_a, = global_axes.plot([calculate_x(event_a.get_ydata(), event_a.get_xdata(), β)], [calculate_t(event_a.get_ydata(), event_a.get_xdata(), β)], marker="o", linestyle="")
        temp.remove()

        temp = a_annotation
        x_location = event_a.get_xdata()
        y_location = event_a.get_ydata()

        # do something with the annotation
        a_annotation = global_axes.annotate(
            f'A: ({y_location}, {x_location})',
            xy=(x_location, y_location), 
            xytext=(x_location + 2 * 0.25, y_location + 2 * 0.5), 
            arrowprops=dict(facecolor='black', shrink=2 * 0.1), # Arrow properties
            bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="black", lw=1, alpha=0.9), # Text box properties
            ha='left', va='bottom'
        )

        temp.remove()

    if (event_b != None and β != None):
        print("Do something for event B")

    figure.draw_idle()

def add_lorentz_curves(global_axes, intervals=None):
    global color_index, color_options, t, x
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

    t = global_axes.axvline(x=0, color='black', linestyle="-", label='x')
    x = global_axes.axhline(y=0, color='black', linestyle="-", label='t')


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

        global_axes.plot(x_vals, y, color=color_options[color_index], linestyle="-", alpha=alpha)
        global_axes.plot(x_vals, -y, color=color_options[color_index], linestyle="-", alpha=alpha)

        global_axes.plot(x_branch, y_vals, color=color_options[color_index], linestyle="-", alpha=alpha)
        global_axes.plot(-x_branch, y_vals, color=color_options[color_index], linestyle="-", alpha=alpha)

        if (color_index < 6):
            color_index += 1
        else:
            color_index = 0

def remove_frame(figure):
    global tprime, xprime
    if tprime is not None:
        tprime.remove()
        tprime = None
    if xprime is not None:
        xprime.remove()
        xprime = None

    figure.draw_idle()

def remove_function(figure):
    global point, point_line
    if point is not None:
        point.remove()
        point = None
    if point_line is not None:
        point_line.remove()
        point_line = None

    figure.draw_idle()

def remove_a(figure):
    global event_a, a_annotation
    if event_a is not None:
        event_a.remove()
        event_a = None
    if a_annotation is not None:
        a_annotation.remove()
        a_annotation = None

    figure.draw_idle()

def remove_b(figure):
    global event_b, b_annotation
    if event_b is not None:
        event_b.remove()
        event_b = None
    if b_annotation is not None:
        b_annotation.remove()
        b_annotation = None

    figure.draw_idle()


def calculate_frame(x_intercept, β_provided, global_axes):
    global tprime, xprime, β, x_new_frame
    x_new_frame = x_intercept

    if (tprime != None or xprime != None):
        tprime.remove()
        tprime = None
        xprime.remove()
        xprime = None

    β = β_provided
    if (β >= 1 or β <= -1):
        raise ValueError(f"β cannot be greater than, less than, or equal to speed of light")
    
    x = (np.linspace(-β - 50, β + 50, 4000))

    slope = (1 / β)

    equation_t = (slope * x) - (x_intercept / β)
    equation_x = (β * x) - (x_intercept * β)

    tprime_line, = global_axes.plot(x, equation_t, color="blue", label="t'")
    xprime_line, = global_axes.plot(x, equation_x, color="orange", label="x'")

    # Enable pick events so gui.move_factory onpick sees these lines as artists
    tprime_line.set_picker(5)
    xprime_line.set_picker(5)

    tprime = tprime_line
    xprime = xprime_line

def calculate_t(tprime, xprime, β):
    γ = 1 / (math.sqrt(1 - (math.pow(β, 2))))

    return γ * (tprime + (β * xprime))

def calculate_x(tprime, xprime, β):
    γ = 1 / (math.sqrt(1 - (math.pow(β, 2))))

    return γ * ((β * tprime) + xprime)

def calculate_t_prime(t, x, β):
    γ = 1 / (math.sqrt(1 - (math.pow(β, 2))))

    return γ * (t - (β * x))

def calculate_x_prime(t, x, β):
    γ = 1 / (math.sqrt(1 - (math.pow(β, 2))))

    return γ * ((-β * t) + x)
