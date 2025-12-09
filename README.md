# FrameCalc
## _Spacetime relativity simulator_

![FrameCalc demo]([(https://github.com/shworm/spacetime-diagram/blob/main/demogif.gif)])


[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)

FrameCalc is a spacetime graphing calculator for special relativity.
- Plot worldlines for objects and observers
- Transform between reference frames using Lorentz boosts
- Visualize time dilation, length contraction, and simultaneity
- Compare events across different frames of reference at different speeds

## Features

Built on the Python library matploblib, FrameCalc adds increasd functionality to allow for an easier user experience modeling relativity. 
> Click and drag for panning, while maintaining graph ticks
> Mouse scroll to zoom in and out, scaling the axis
> Model two observer diagrams, and transform between them
> Clicking to view the specific position of events and worldlines 
> Model multiple events through spacetime

## Packages

Dillinger uses a number of python libraries:

- [NumPy] - For several processes, including the panning system I developed for user interaction
- [Matploblib] - The foundation of the graph
- [math] - To accuratly transform points and worldlines
- [Tkinter / FigureCanvasTkAgg] - UI and input interface

## Installation

Download the most recent demo here:
[Download v1.0.0](https://github.com/shworm/spacetime-diagram/releases/download/release/spacetime-demo.zip)

## Use cases / acknowledgement
Thanks to Seth Kimbrell (https://www.linkedin.com/in/seth-kimbrell-ph-d-698b7a75/) for your class on Special Relativity. I hope this project is useful for educating students on the principals of relativity in the future.
