"""
The abstract class for an App related to transit.
"""


class TransitPredictionsApp:
    """
    An app that fetches transit predictions and displays them.
    """

    def update(self) -> int:
        """
        Updates predictions and the display with these new predictions.

        :return: the time to wait until the next update
        """

        raise NotImplementedError("Subclasses of TransitPredictionsApp must implement the update() method")
