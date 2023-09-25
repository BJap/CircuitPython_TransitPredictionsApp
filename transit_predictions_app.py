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
        Construct a new 'TransitPredictionsApp' object using a data source and output display.

        :param requests: the requests object with which to fetch predictions
        """
        
        self.__display = transit_predictions_app_io.get_display()
        self.__source = transit_predictions_app_io.get_source(requests)

    def run(self):
        """
        Runs the TransitPredictionsApp app.
        """
        
        while True:
            predictions = self.__source.get_predictions()
            wait = self.__source.get_refresh_interval()

            self.__display.show(predictions)

            print(f'Refreshing predictions in {wait} seconds\n')

            sleep(wait)
