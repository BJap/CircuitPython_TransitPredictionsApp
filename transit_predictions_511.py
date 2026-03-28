"""
The controller to fetch predictions, display them, and notify when to update again.
"""

from gc import collect
from zlib import decompress

# local
from config import DEBUG_MODE

ERROR_REFRESH_SEC = 30
MAX_REFRESH_SEC = 60
MIN_REFRESH_SEC = 10


class TransitPredictions511:
    """
    A class for the TransitPredictionsApp to use for its source data.
    """

    def __init__(
            self,
            display,
            source,
            agency,
            stop_code,
            route_codes,
            directions
    ):
        """
        Constructs a predictions object to feed data to the TransitPredictionsApp.

        :param display: the object that shows the transit predictions
        :param source: the object that fetches and models transit predictions
        :param agency: the agency that has the predictions
        :param stop_code: the stop for which to gather predictions
        :param route_codes: the routes of interest
        :param directions: the directions of interest
        """

        self._agency = agency
        self._display = display
        self._directions = set(directions.split(','))
        self._route_codes = route_codes
        self._source = source
        self._stop_code = stop_code

        self._data_handler = source.get_data_handler()

    @staticmethod
    def _check_for_success(status_code):
        """
        Checks the response for a success.

        :param status_code: the status code to check
        :return: whether the status code indicates a success
        """

        return 200 <= status_code < 300

    def _get_predictions(self):
        """
        Gets the predictions for the PredictionsApp.

        :return: the lines of text to display in format of:
            - <route code> <route title>
            - <prediction 1> <prediction 2> ...
        """

        predictions = self._data_handler.predictions_for_route_codes(
            self._data,
            self._route_codes,
            self._directions
        )
        prediction_text = []

        if predictions:
            for route_code in self._route_codes:
                if route_code in predictions:
                    route = predictions[route_code]

                    prediction_text.extend(self._display.formatter.format(route))

        if DEBUG_MODE:
            if prediction_text:
                for text in prediction_text:
                    print(text)

                print('')
            else:
                print('No predictions available\n')

        return prediction_text

    def _get_refresh_interval(self):
        """
        Gets when the next refresh of prediction data should occur.

        :return: the minimum time, the time until the next transit arrives, or the maximum time (in seconds)
        """

        seconds_soonest = self._data_handler.prediction_seconds_soonest(
            self._data,
            self._route_codes,
            self._directions
        )

        if not seconds_soonest:
            if DEBUG_MODE:
                print('There are no desired transit options arriving soon\n')

            return MAX_REFRESH_SEC

        if DEBUG_MODE:
            print(f'The next desired transit option arrives in {seconds_soonest} seconds\n')

        return max(min(seconds_soonest, MAX_REFRESH_SEC), MIN_REFRESH_SEC)

    def _poll(self):
        """
        Polls for prediction data and stores it at class level.
        """

        # Wipe the existing data and fetch new data
        self._data = None
        response = self._source.predictions_for_stop_code(self._agency, self._stop_code)
        self._status_code = response.status_code
        self._reason = response.reason.decode('utf-8')

        if self._check_for_success(self._status_code):
            data = decompress(response.content, 31)[3:].decode('utf-8')
            self._data = self._data_handler.parse_data(data)
        elif DEBUG_MODE:
            print(f'Status code: {self._status_code}\n')
            print(f'Reason: {self._reason}\n')

        response.close()

        # Free up all this memory or the next poll's allocation will fail on some devices
        del response
        del data
        collect()

    def update(self):
        '''
        Updates predictions and the display with thse new predictions.
        '''

        if DEBUG_MODE:
            print(f'Getting predictions for agency {self._agency} for stop_code {self._stop_code}')

        self._poll()

        # Polling failed
        if not self._data:
            self._display.show(['Network Error', f'{self._status_code}', f'{self._reason}'])

            return ERROR_REFRESH_SEC

        self._display.show(self._get_predictions())

        return self._get_refresh_interval()
