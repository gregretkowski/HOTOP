HOTOP: Hands On Throttle Or Pointer

HOTOP is a system to provide easy interaction with the controls
inside of VR. It was developed for DCS but could probably work
with any software that allows VR interaction via mouse.

The system consists of an IR camera mounted on your VR headset
and a glove worn on your throttle hand. The glove is USB powered,
has two mouse buttons and three IR LED's. Based on your hand
position and button presses you can interact with the interior
of a VR environment as if using a mouse.

NOTE: This is a Proof-of-Concept / early prototype. To have any
hope of getting this to work yourself you should be experienced
at hacking on python, building electronic circuits, and CAD 3D
prints. No support is offered.

# FUTURE TODO

* lots of code cleanup
* write unit tests
* build pipeline (github actions?)
* package as an executable
* build a UI via Kivy
* auto-calibration by clicking left-center, top-center, right-center
* smoothing algorithms & reliability tuning
* someone go make some HW / CAD / 3D printable designs

# Hardware and Protocol

The needed hardware includes an IR camera, and a glove which illuminates
IR LED's indicating pointer moves or mouse clicks.

The protocol is very simple. If a single point is seen the pointer is
moved to the location of that point. If two points are seen for a brief
period a left-click is sent. If two points are seen for a longer period
scroll-down events are sent. If three points are seen briefly a
right-click is sent, three points for longer scroll-up events are sent.

It was designed to keep the hardware as simple as possible.

The camera used for the prototype:

https://www.amazon.com/gp/product/B09CTTBZY3

IFWATER 1MP USB Camera Module, Wide Angle Lens USB Webcam with 1/4" CMOS OV9712 Sensor,720P 100 Degree USB Webcam Supports OS,USB2.0 High Speed Plug and Play for Industrial Machine Vision

To create a visible-light-filter, lighting gel's were used, with a red
and blue gel stacked over the camera.

https://www.amazon.com/gp/product/B07PY7NBST

SAKOLLA 8 Pieces Transparent Color Correction Lighting Gel Filter - Colored Gel Light Filter Plastic Sheet, 8.5 x 11 Inch, 8 Assorted Colors

The prototype glove was built using Adafruit Super-bright 5mm IR LED's [ADA388]
The LED's were filed down to widen their beam angle (just cause thats what
I had on-hand). See the docs folder for an image of the circuit and photo
of the glove.

There are some things I'll do in the next glove to improve performance
* Ensure LED's are angled away from the hand (30deg?)
* that the LED's used have a wide beam.
* Make the three LED's further from each other.

The HW specification is 'free and open' and anyone is welcome to
make and sell kits or completed hardware. The author may be one
of your first customers.

# Developing

Launch from 'conda' launcher - expects python 3.
Launch your DCS window
edit config.yml - restart app whenever changing the config

    cd into dir
    # just once
    python -m venv venv
    .\venv\Scripts\activate
    # just once
    pip install -r requirements.txt
    python main.py
