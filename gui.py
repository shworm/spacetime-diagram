import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

import core


def submit_function(x, canvas):
    try:
        float(x)
    except ValueError:
        raise ValueError(f"Cannot convert '{x}' to a float.")
    
    x = float(x)
    core.add_point(x)
    canvas.draw_idle()

def stop(window):
    window.destroy() 
    core.stop()

def main():
    # This is where we do all of our tkinter stuff
    window = tk.Tk()
    window.title("Spacetime Diagram")
    window.geometry("1000x1000")

    greeting = tk.Label(window, text="Object's x location")
    greeting.pack()

    input = tk.Entry(window, text="Enter here: ", bg="white", fg="black")
    input.pack()

    submit_button = tk.Button(window, text="Submit", command=lambda: submit_function(input.get(), canvas))
    submit_button.pack()    

    # closes the window
    quit_button = tk.Button(window, text="Quit", command=lambda: stop(window))
    quit_button.pack()

    # Here we make the actual matplotlib graph
    figure = core.create_graph()
    canvas = FigureCanvasTkAgg(figure, master=window)
    canvas.draw_idle() # draw it
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10) # what does this do?

    # bind global_axes events to these ones we are defining in these functions
    core.zoom_factory(core.global_axes)
    core.move_factory(core.global_axes)

    # main event loop
    window.mainloop()
