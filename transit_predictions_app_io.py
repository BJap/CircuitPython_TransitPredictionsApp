"""
This file is used to provide a model view and controller for IO for the
TransitPredictionsApp. These are made to be swappable so the end user can
configure the app to work with different prediction APIs and display
devices. Replace with any self-written file that matches the API and
hardware used if not the same as below.

This configuration is set to use the 511.org API with a 64x32 RGB LED Matrix
powered by a Matrix Portal S3 (ESP32-S3).

It uses dependencies from adafruit-circuitpython-bundle-8.x found at:
https://circuitpython.org/libraries

and a font from Dr Markus Kuhn's website
https://www.cl.cam.ac.uk/~mgk25/ucs-fonts.html

specifically this font:
https://opensource.apple.com/source/X11fonts/X11fonts-14/font-misc-misc/font-misc-misc-1.1.2/5x7.bdf.auto.html
"""

from displayio import Group
from os import getenv

# libs
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text import label
from adafruit_matrixportal.matrix import Matrix

# local
from display import Sign
from transit_api_511 import TransitApi
from transit_predictions_511 import TransitPredictions511

PANEL_WIDTH = 64
PANEL_HEIGHT = 32

COLOR_LINE_TEXT = 0x4F1400

MAX_PREDICTIONS = 2

TEXT_FONT = 'fonts/5x7.bdf'
TEXT_FONT_WIDTH = 5
TEXT_FONT_HEIGHT = 7


def get_display():
    """
    Gets the display that will show the predictions. The source needs to
    have one method:
        show(text: [str])

    :return: the display object
    """

    font = bitmap_font.load_font(TEXT_FONT)
    
    # Transit line 1 and predictions
    line1 = label.Label(font)
    line1.color = COLOR_LINE_TEXT
    line1.text = 'Predictions'
    line1.x = 0
    line1.y = 3
    
    # Transit line 2 and predictions
    line2 = label.Label(font)
    line2.color = COLOR_LINE_TEXT
    line2.text = 'for SF MUNI'
    line2.x = 0
    line2.y = line1.y + TEXT_FONT_HEIGHT + 1
    
    middle = int(PANEL_HEIGHT / 2)
    
    # Transit line 3 and predictions
    line3 = label.Label(font)
    line3.color = COLOR_LINE_TEXT
    line3.text = 'using API'
    line3.x = 0
    line3.y = middle + 3
    
    # Transit line 4 and predictions
    line4 = label.Label(font)
    line4.color = COLOR_LINE_TEXT
    line4.text = '511.org'
    line4.x = 0
    line4.y = line3.y + TEXT_FONT_HEIGHT + 1

    g = Group()
    g.append(line1)
    g.append(line2)
    g.append(line3)
    g.append(line4)

    # Matrix Portal S3 (ESP32-S3)
    display = Matrix(bit_depth=6).display
    display.refresh(minimum_frames_per_second=0)
    # change this to 180 to plug power in from the left rather than the right
    display.rotation = 0
    display.show(g)

    return Sign(display, [line1, line2, line3, line4])


def get_source(requests):
    """
    Gets the source object used to fetch and model predictions.

    :param requests: the requests object with which to fetch predictions
    :return: the source object
    """

    return TransitApi(requests, getenv('511_API_KEY'), 'json')


def get_controller(display, source):
    """
        Gets the controller used to fetch and display predictions. The source needs
        to have one method to update the info and return when to update next (in seconds):
            update(): int

    :param requests: the requests object with which to fetch predictions
    :return: the predictions controller object
    """

    return TransitPredictions511(
        display,
        source,
        getenv('511_TRANSIT_AGENCY'),  # agency
        getenv('511_TRANSIT_STOP_CODE'),  # stop_code
        getenv('511_TRANSIT_ROUTE_CODES').split(','),  # route_codes
        getenv('511_TRANSIT_DIRECTION'),  # direction
        MAX_PREDICTIONS  # max_predictions
    )

