"""
This file is used to print messages only while debugging.
"""

# local
from config import DEBUG_MODE


def log(message: str):
    """
    Prints a message while debugging, and nothing otherwise.

    :param message: the message to print
    """

    # Logging is on.
    if DEBUG_MODE:
        print(message)
