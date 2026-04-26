"""
Display types that can be used to present prediction data
"""

# lib
from adafruit_display_text.label import Label
from adafruit_matrixportal.matrix import Matrix

# local
from transit.prediction_formatter import TransitPredictionFormatter


class Display:
    """
    Used to display text to a given output.
    """

    def show(self, text: list[str]):
        """
        Shows the provided text.

        :param text: an array of text to display
        """

        raise NotImplementedError("Subclasses of Display must implement the show() method")


class DisplayConfigration:
    """
    Used to create the display and hold its configuration
    """

    @staticmethod
    def get_display() -> Display:
        """
        Gets the display that will show the predictions. The display needs to
        have one method:
            show(text: list[str])

        :return: the display object
        """

        raise NotImplementedError("Subclasses of DisplayConfigration must implement the get_display() method")

    @staticmethod
    def get_formatter() -> TransitPredictionFormatter:
        """
        Gets a formatter to prepare 'Route' information for the display.

        :return: a transit prediction formatter as default or custom if overridden
        """

        return TransitPredictionFormatter()

    @property
    def maximum_predictions(self) -> int:
        """
        Determines how many predictions will be displayed at most per transit line.

        :return: the prediction count
        """

        raise NotImplementedError("Subclasses of DisplayConfigration must implement the prediction_count property")

    @property
    def show_titles(self) -> bool:
        """
        Determines whether the title will be displayed per transit line.

        :return: true if the titles should be shown
        """

        raise NotImplementedError("Subclasses of DisplayConfigration must implement the show_titles property")


class Console(Display):
    """
    Used to print to the REPL console. This is good for debugging changes
    or writing a new predictions object without using any hardware.
    """

    def show(self, text: list[str]):
        for label in text:
            print(label)


class Sign(Display):
    """
    Prints text to an RGBMatrix
    """

    def __init__(self, matrix: Matrix, labels: list[Label]):
        """
        Constructs a 'Sign' object to display text.

        :param matrix: the display matrix on which to show text
        :param labels: the labels provided in the display
        """

        self._labels = labels

        self.matrix = matrix

    def show(self, text: list[str]):
        # Wipe the existing text from the labels.
        for label in self._labels:
            label.text = ''

        n = min(len(self._labels), len(text))
        i = 0

        # Set the new texts to each label.
        while i < n:
            self._labels[i].text = text[i]
            i += 1
