"""
Display types that can be used to present prediction data
"""


class Console:
    """
    Used to display to the REPL console. This is good for debugging changes
    or writing a new predictions object without using the sign.
    """

    def __init__(self, formatter):
        """
        Constructs a 'Console' object to print text.

        :param formatter: the formatter used to prepare the text to display
        """

        self.formatter = formatter

    def show(self, text):
        """
        Shows the provided text.

        :param text: an array of text to display
        """

        for line in text:
            print(line)


class Sign:
    """
    Prints text to an RGBMatrix
    """

    def __init__(self, display, formatter, lines):
        """
        Constructs a 'Sign' object to display text.

        :param display: the display matrix on which to show text
        :param formatter: the formatter used to prepare the text to display
        :param lines: the lines provided in the display
        """

        self.__lines = lines

        self.display = display
        self.formatter = formatter

    def show(self, text):
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
