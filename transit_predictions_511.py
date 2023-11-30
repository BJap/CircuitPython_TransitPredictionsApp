"""
The controller to fetch predictions, display them, and notify when to update again.
"""

from gc import collect
from zlib import decompress

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
            direction
    ):
        """
        Constructs a predictions object to feed data to the TransitPredictionsApp.

        :param display: the object that shows the transit predictions
        :param source: the object that fetches and models transit predictions
        :param agency: the agency that has the predictions
        :param stop_code: the stop for which to gather predictions
        :param route_codes: the routes of interest
        :param direction: the direction of interest
        """

        self.__agency = agency
        self.__display = display
        self.__direction = direction
        self.__route_codes = route_codes
        self.__source = source
        self.__stop_code = stop_code

        self.__data_handler = source.get_data_handler()

    @staticmethod
    def __check_for_success(status_code):
        """
        Checks the response for a success.

        :param status_code: the status code to check
        :return: whether the status code indicates a success
        """

        return 200 <= status_code < 300

    def __get_predictions(self):
        """
        Gets the predictions for the PredictionsApp.

        :return: the lines of text to display in format of:
            - <route code> <route title>
            - <prediction 1> <prediction 2> ...
        """

        predictions = self.__data_handler.predictions_for_route_codes(
            self.__data,
            self.__route_codes,
            self.__direction
        )
        prediction_text = []

        if predictions:
            for route_code in self.__route_codes:
                if route_code in predictions:
                    route = predictions[route_code]

                    prediction_text.extend(self.__display.formatter.format(route))

        if prediction_text:
            for text in prediction_text:
                print(text)

            print('')
        else:
            print('No predictions available\n')

        return prediction_text

    def __get_refresh_interval(self):
        """
        Get when the next refresh of prediction data should occur.

        :return: the minimum time, the time until the next transit arrives, or the maximum time (in seconds)
        """

        seconds_soonest = self.__data_handler.prediction_seconds_soonest(
            self.__data,
            self.__route_codes,
            self.__direction
        )

        if not seconds_soonest:
            print('There are no desired transit options arriving soon\n')

            return MAX_REFRESH_SEC

        print(f'The next desired transit option arrives in {seconds_soonest} seconds\n')

        return max(min(seconds_soonest, MAX_REFRESH_SEC), MIN_REFRESH_SEC)

    def __poll(self):
        """
        Polls for prediction data and stores it at class level.
        """

        # Wipe the existing data and fetch new data
        self.__data = None
        response = self.__source.predictions_for_stop_code(self.__agency, self.__stop_code)
        self.__status_code = response.status_code
        self.__reason = response.reason.decode('utf-8')

        if self.__check_for_success(self.__status_code):
            # There's a bug for this that was fixed in
            # https://github.com/adafruit/circuitpython/pull/8335
            # Then this will probably become:
            # data = decompress(response.content, 31).decode('utf-8')
            data = decompress(response.content[10:], -31)[3:].decode('utf-8')
            self.__data = self.__data_handler.parse_data(data)
        else:
            print(f'Status code: {self.__status_code}\n')
            print(f'Reason: {self.__reason}\n')

        response.close()

        # Free up all this memory or the next poll's allocation will fail on some devices
        del response
        del data
        collect()

    def update(self):
        print(f'Getting predictions for agency {self.__agency} for stop_code {self.__stop_code}')

        self.__poll()

        # Polling failed
        if not self.__data:
            self.__display.show(['Network Error', f'{self.__status_code}', f'{self.__reason}'])

            return ERROR_REFRESH_SEC

        self.__display.show(self.__get_predictions())

        return self.__get_refresh_interval()
