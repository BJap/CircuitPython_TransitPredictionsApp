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

# lib
from adafruit_bitmap_font import bitmap_font
from adafruit_display_shapes.line import Line
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrix import Matrix

# local
from display.display import Display, DisplayConfigration, Sign

COLOR_SEPARATOR = 0x00071F
COLOR_LINE_TEXT = 0x4F1400
COLOR_PREDICTION_TEXT = 0x001800

PANEL_WIDTH = 64
PANEL_HEIGHT = 32

TEXT_FONT = 'fonts/5x7.bdf'
TEXT_FONT_WIDTH = 5
TEXT_FONT_HEIGHT = 7


class ConfigurationMatrix64X32Fancy(DisplayConfigration):
    @staticmethod
    def get_display() -> Display:
        font = bitmap_font.load_font(TEXT_FONT)

        # Transit Label 1
        label1 = Label(font)
        label1.color = COLOR_LINE_TEXT
        label1.x = 0
        label1.y = 3

        # Prediction line 1
        label2 = Label(font)
        label2.color = COLOR_PREDICTION_TEXT
        label2.x = 0
        label2.y = label1.y + TEXT_FONT_HEIGHT + 1

        middle = int(PANEL_HEIGHT / 2)

        # Separator line
        separator = Line(0, middle - 1, PANEL_WIDTH, middle - 1, COLOR_SEPARATOR)

        # Transit line 2
        label3 = Label(font)
        label3.color = COLOR_LINE_TEXT
        label3.x = 0
        label3.y = middle + 4

        # Prediction line 2
        label4 = Label(font)
        label4.color = COLOR_PREDICTION_TEXT
        label4.x = 0
        label4.y = label3.y + TEXT_FONT_HEIGHT + 1

        g = Group()
        g.append(label1)
        g.append(label2)
        g.append(separator)
        g.append(label3)
        g.append(label4)

        # Matrix Portal S3 (ESP32-S3)
        matrix = Matrix(bit_depth=6).display
        matrix.refresh(minimum_frames_per_second=0)
        # Change this to 0 to plug power in from the right rather than the left.
        matrix.rotation = 180
        matrix.root_group = g

        return Sign(matrix, [label1, label2, label3, label4])

    @property
    def maximum_predictions(self) -> int:
        return 3

    @property
    def show_titles(self) -> bool:
        return True
