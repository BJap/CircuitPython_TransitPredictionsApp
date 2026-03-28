"""
Apps related to transit.
"""

from time import sleep

# local
from config import DEBUG_MODE
import transit_predictions_app_io


class TransitPredictionsApp:
    """
    An app that fetches transit predictions and displays them.
    """

    def __init__(self, requests):
        """
        Construct a new 'TransitPredictionsApp' object using a data source and output display
        with a controller.

        :param requests: the requests object with which to fetch predictions
        """

        display = transit_predictions_app_io.get_display()
        source = transit_predictions_app_io.get_source(requests)

        self._controller = transit_predictions_app_io.get_controller(display, source)

    def run(self):
        """
        Runs the TransitPredictionsApp app.
        """

        while True:
            wait = self._controller.update()

            if DEBUG_MODE:
                print(f'Refreshing predictions in {wait} seconds\n')

            sleep(wait)
