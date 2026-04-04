"""
Display types that can be used to present prediction data
"""

# lib
from adafruit_matrixportal.matrix import Matrix


class Display:
    """
    Used to display text to a given output.
    """

    def show(self, text: list[str]):
        """
        Shows the provided text.

        :param text: an array of text to display
        """

        raise NotImplementedError("Subclasses of Display must implement show() method")

class Console(Display):
    """
    Used to print to the REPL console. This is good for debugging changes
    or writing a new predictions object without using any hardware.
    """

    def show(self, text: list[str]):
        """
        Shows the provided text.

        :param text: an array of text to display
        """

        for line in text:
            print(line)


class Sign(Display):
    """
    Prints text to an RGBMatrix
    """

    def __init__(self, matrix: Matrix, lines):
        """
        Constructs a 'Sign' object to display text.

        :param matrix: the display matrix on which to show text
        :param lines: the lines provided in the display
        """

        self.__lines = lines

        self.matrix = matrix

    def show(self, text: list[str]):
        """
        Shows the provided text.

        :param text: an array of text to display
        """

        # Wipe the existing text from the lines
        for line in self.__lines:
            line.text = ''

        n = min(len(self.__lines), len(text))
        i = 0

        # Set the new texts to each line
        while i < n:
            self.__lines[i].text = text[i]
            i += 1
