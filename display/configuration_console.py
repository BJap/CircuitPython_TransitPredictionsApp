"""
This file is used to provide a model view and controller for IO for the
TransitPredictionsApp. These are made to be swappable so the end user can
configure the app to work with different prediction APIs and display
devices. Replace with any self-written file that matches the API and
hardware used if not the same as below.
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
