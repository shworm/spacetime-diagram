import math

def create_worldline(x_intercept, velocity, axes):
    if (velocity > 1 or velocity < -1):
        raise ValueError("Velocity cannot be faster than the speed of light.")
    elif (velocity == -1 or velocity == 1):
        print("do something special")
    else:
        print("do something normal")