"""
The abstract class for transit API interaction.
"""

# lib
from adafruit_requests import Response

# local
from transit.data_handler import TransitDataHandler


class TransitAPI:
    """
    All the API calls are made from this class.
    """
    @staticmethod
    def check_for_success(status_code: int) -> bool:
        """
        Checks the response for a success.

        :param status_code: the status code to check
        :return: whether the status code indicates a success
        """

        return 200 <= status_code < 300

    def get_data_handler(self) -> TransitDataHandler:
        """
        Gets the handler to parse the data returned from the API in the chosen format.

        :return: the data handler
        """

        raise NotImplementedError("Subclasses of TransitAPI must implement the get_data_handler() method")

    def get_predictions(self, config: tuple[str, ...]) -> Response:
        """
        Makes a request for the predictions at a given stop.

        :param config: the config that specifies what to predict
        :return: the request response
        """

        raise NotImplementedError("Subclasses of TransitAPI must implement the get_predictions() method")
