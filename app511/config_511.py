"""
The configuration for which to get predictions from 511.org.
"""

from os import getenv


class TransitConfig511:
    """
    Holds the configuration for fetching predictions.
    """

    def __init__(self, api_key: str, agency: str, directions: str, route_codes: str, stop_code: str):
        """
        Construct a new 'TransitConfig511' object using the provided configuration.

        :param agency: the transit agency
        :param directions: the directions (could be one direction, the other, or both)
        :param route_codes: the routes of interest
        :param stop_code: the stop for the arrivals
        """

        self.agency = agency
        self.api_key = api_key
        self.directions =  directions.split(',')
        self.route_codes = route_codes.split(',')
        self.stop_code = stop_code

    @staticmethod
    def from_environment():
        """
        Constructs a 'TransitConfig511' object using environmental variables.

        :return: an instance of this class
        """

        return TransitConfig511(
            getenv('511_API_KEY'),
            getenv('511_TRANSIT_AGENCY'),  # agency
            getenv('511_TRANSIT_DIRECTIONS'),  # directions
            getenv('511_TRANSIT_ROUTE_CODES'),  # route_codes
            getenv('511_TRANSIT_STOP_CODE')  # stop_code
        )
