"""
The app to fetch predictions, display them, and notify when to update again.
"""

from gc import collect
from zlib import decompress

# lib
from adafruit_requests import Session

# local
from app511.api_511 import TransitAPI511
from app511.config_511 import TransitConfig511
from config import DEBUG_MODE
from display.display import DisplayConfigration
from transit.predictions_app import TransitPredictionsApp

# SOURCE

RESPONSE_FORMAT = 'json'

# UPDATE

ERROR_REFRESH_SEC = 30
MAX_REFRESH_SEC = 60
MIN_REFRESH_SEC = 10


class TransitPredictionsApp511(TransitPredictionsApp):
    """
    An app that fetches transit predictions from 511.org and displays them.
    """

    def __init__(
            self,
            requests: Session,
            display_config: DisplayConfigration,
            api_config: TransitConfig511=TransitConfig511.from_environment()
    ):
        """
        Construct a new 'TransitPredictionsApp511' object using a data source and output display
        with a controller.

        :param requests: the requests object
        :param display_config: the configuration for the display
        :param api_config: the configuration for the api
        """

        self._api_config = api_config
        self._display_config = display_config

        self._display = display_config.get_display()
        self._display.show(['Predictions', 'for SF MUNI', 'using API', '511.org'])

        self._formatter = display_config.get_formatter()
        self._source = TransitAPI511(requests, api_config.api_key, RESPONSE_FORMAT)


    def _get_predictions(self) -> list[str]:
        """
        Gets the predictions for the app.

        :return: the lines of text to display in format of:
            - <route code> <route title>
            - <prediction 1> <prediction 2> ...
        """

        predictions = self._source.get_data_handler().extract_predictions(
            self._data,
            (self._api_config.route_codes, self._api_config.directions)
        )
        prediction_text = []

        if predictions:
            for route_code in self._api_config.route_codes:
                if route_code in predictions:
                    route = predictions[route_code]
                    route_text = self._formatter.format(
                        route,
                        self._display_config.maximum_predictions,
                        self._display_config.show_titles
                    )

                    prediction_text.extend(route_text)

        if DEBUG_MODE:
            if prediction_text:
                for text in prediction_text:
                    print(text)

                print('')
            else:
                print('No predictions available\n')

        return prediction_text

    def _get_refresh_interval(self) -> int:
        """
        Gets when the next refresh of prediction data should occur.

        :return: the minimum time, the time until the next transit arrives, or the maximum time (in seconds)
        """

        seconds_soonest = self._source.get_data_handler().extract_seconds_soonest(
            self._data,
            (self._api_config.route_codes, self._api_config.directions)
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

        # Wipe the existing data and fetch new data.
        self._data = None
        response = self._source.get_predictions((self._api_config.agency, self._api_config.stop_code))
        self._status_code = response.status_code
        self._reason = response.reason.decode('utf-8')

        if TransitAPI511.check_for_success(self._status_code):
            data = decompress(response.content, 31)[3:].decode('utf-8')
            self._data = self._source.get_data_handler().parse_data(data)
        elif DEBUG_MODE:
            print(f'Status code: {self._status_code}\n')
            print(f'Reason: {self._reason}\n')

        response.close()

        # Free up all this memory or the next poll's allocation will fail on some devices.
        del response
        del data
        collect()

    def update(self) -> int:
        """
        Updates predictions and the display with these new predictions.
        """

        if DEBUG_MODE:
            print(
                f'Getting predictions for agency {self._api_config.agency} for stop_code {self._api_config.stop_code}'
            )

        self._poll()

        # Polling failed.
        if not self._data:
            self._display.show(['Network Error', f'{self._status_code}', f'{self._reason}'])

            return ERROR_REFRESH_SEC

        self._display.show(self._get_predictions())

        return self._get_refresh_interval()
