"""
Apps related to transit.
"""

from time import sleep

# local
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

        self.__controller = transit_predictions_app_io.get_controller(display, source)

    def run(self):
        """
        Runs the TransitPredictionsApp app.
        """
        
        while True:
            wait = self.__controller.update()

            print(f'Refreshing predictions in {wait} seconds\n')

            sleep(wait)
