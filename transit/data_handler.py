"""
The abstract class for handling transit data.
"""


class TransitDataHandler:
    """
    Parses the data returned from the API.
    """

    @staticmethod
    def extract_predictions(data: dict, keys: tuple) -> dict:
        """
        Takes all the prediction data and collects only the relevant items.

        :param data: the data to parse
        :param keys: the keys for the relevant predictions
        :return: the predictions that are available if any
        """

        raise NotImplementedError("Subclasses of TransitDataHandler must implement the extract_predictions() method")

    @staticmethod
    def extract_seconds_soonest(data: dict, keys: tuple) -> int | None:
        """
        Determines when the next transit will arrive.

        :param data: the data to parse
        :param keys: the keys for the relevant predictions
        :return: the next arrival time or 0 if there are no predictions
        """

        raise NotImplementedError(
            "Subclasses of TransitDataHandler must implement the extract_seconds_soonest() method"
        )

    @staticmethod
    def parse_data(data: str) -> dict:
        """
        Takes the clear-text response data from an API call and formats it into dict

        :return: the data
        """

        raise NotImplementedError("Subclasses of TransitDataHandler must implement the parse_data() method")
