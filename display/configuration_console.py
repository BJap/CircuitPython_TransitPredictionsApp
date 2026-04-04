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

# local
from display.display import Console, Display, DisplayConfigration


class ConfigurationConsole(DisplayConfigration):
    @staticmethod
    def get_display() -> Display:
        return Console()

    @property
    def maximum_predictions(self) -> int:
        return 5

    @property
    def show_titles(self) -> bool:
        return True
