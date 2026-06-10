"""
All the functionality needed to interact with the 511.org API and parse the data is here.

API reference:
https://511.org/open-data/transit

Current reference:
https://511.org/sites/default/files/2022-11/511%20SF%20Bay%20Open%20Data%20Specification%20-%20Transit.pdf

In order to obtain an access token to use for this API go to:
https://511.org/open-data/token
"""

from json import loads

# lib
from adafruit_datetime import datetime
from adafruit_requests import Response, Session

# local
from transit.api import TransitAPI
from transit.data_handler import TransitDataHandler
from transit.route import Route

BASE_URL = 'api.511.org'


class _JsonHandler(TransitDataHandler):
    """
    Parses the data returned in JSON format from the 511.org API.
    """

    @staticmethod
    def extract_predictions(data: dict, keys: tuple) -> dict[str, Route]:
        """
        Takes all the prediction JSON and collects only the relevant items.

        :param data: the data to parse
        :param keys: the keys for the relevant predictions
        :return: the predictions that are available if any
        """

        if not data or not isinstance(data, dict):
            return {}

        # The list of upcoming visits to the stop in the predictions.
        service_delivery: dict = data.get("ServiceDelivery", {})
        stop_monitoring_delivery: dict = service_delivery.get("StopMonitoringDelivery", {})
        visits: list = stop_monitoring_delivery.get("MonitoredStopVisit", [])

        if not visits:
            return {}

        route_codes: list[str] = keys[0]
        directions: list[str] = keys[1]
        now = _JsonHandler._extract_now(data)
        predictions = {}

        # Iterate over all the upcoming visits and gather predictions.
        for visit in visits:
            trip: dict = visit.get('MonitoredVehicleJourney', {})
            route_code: str = trip.get('LineRef')
            direction: str = trip.get('DirectionRef')

            # The route code or direction does not exist.
            if not route_code or not direction:
                continue

            # The route code is not of interest in the trip or not in the correct direction(s).
            if route_code not in route_codes or direction not in directions:
                continue

            # The predicted time of the visit.
            prediction_info: dict = trip.get('MonitoredCall', {})
            arrival_time: str = prediction_info.get('ExpectedArrivalTime')

            if not arrival_time:
                continue

            # CircuitPython only parses DateTime from iso formats without the 'T' and 'Z' in them.
            arrival_time = arrival_time.replace('T', ' ').replace('Z', '')

            try:
                prediction = datetime.fromisoformat(arrival_time)
            except ValueError:
                continue

            if prediction <= now:
                continue

            # The minutes until the trip's arrival.
            minutes = int((prediction - now).seconds / 60)

            # The predictions don't have the route in it yet, add it.
            if route_code not in predictions:
                title: str = trip.get('PublishedLineName', route_code)
                route = Route(route_code, title)
                predictions[route_code] = route

            # Add the minutes to the set of predictions.
            predictions[route_code].add_prediction(minutes)

        # Return the predictions for the desired route codes.
        return predictions

    @staticmethod
    def extract_seconds_soonest(data: dict, keys: tuple) -> int | None:
        """
        Determines when the next transit will arrive.

        :param data: the data to parse
        :param keys: the keys for the relevant predictions
        :return: the next arrival time or 0 if there are no predictions
        """

        if not data or not isinstance(data, dict):
            return None

        # The list of upcoming visits to the stop in the predictions.
        service_delivery: dict = data.get("ServiceDelivery", {})
        stop_monitoring_delivery: dict = service_delivery.get("StopMonitoringDelivery", {})
        visits: list = stop_monitoring_delivery.get("MonitoredStopVisit", [])

        if not visits:
            return None

        route_codes: list[str] = keys[0]
        directions: list[str] = keys[1]
        now = _JsonHandler._extract_now(data)
        soonest_seconds = None

        # Iterate over all the upcoming visits and find the soonest arrival of desired route codes.
        for visit in visits:
            trip: dict = visit.get('MonitoredVehicleJourney', {})
            route_code: str = trip.get('LineRef')
            direction: str = trip.get('DirectionRef')

            # The route code or direction does not exist.
            if not route_code or not direction:
                continue

            # The route code is not of interest in the trip or not in the correct direction(s).
            if route_code not in route_codes or direction not in directions:
                continue

            # The predicted time of the visit.
            prediction_info: dict = trip.get('MonitoredCall', {})
            arrival_time: str = prediction_info.get('ExpectedArrivalTime')

            if not arrival_time:
                continue

            # CircuitPython only parses DateTime from iso formats without the 'T' and 'Z' in them.
            arrival_time = arrival_time.replace('T', ' ').replace('Z', '')

            try:
                prediction = datetime.fromisoformat(arrival_time)
            except ValueError:
                continue

            if prediction <= now:
                continue

            seconds_diff = int((prediction - now).seconds)

            # Keep the smallest wait time value found across all valid routes
            if soonest_seconds is None or seconds_diff < soonest_seconds:
                soonest_seconds = seconds_diff

        return soonest_seconds

    @staticmethod
    def _extract_now(data: dict) -> datetime:
        """
        Takes all the prediction JSON and collects the service's current date and time.

        :param data: the data to parse
        :return: the datetime
        """

        if not data or not isinstance(data, dict):
            return datetime.now()

        # The time the predictions data was sent.
        # This is used because some predictions come back with a 'created' unix time stamp
        # of 0, so they are inaccurate to use for temporal subtraction so a unified baseline
        # of 'now' is used to get around this flaw in the API response.
        service_delivery: dict = data.get("ServiceDelivery", {})
        stop_monitoring_delivery: dict = service_delivery.get("StopMonitoringDelivery", {})
        data_time: str = stop_monitoring_delivery.get('ResponseTimestamp')

        if not data_time:
            return datetime.now()

        # CircuitPython only parses DateTime from iso formats without the 'T' and 'Z' in them.
        data_time = data_time.replace('T', ' ').replace('Z', '')

        try:
            api_now = datetime.fromisoformat(data_time)

            # Update the device real time clock to the one from 511.org.
            # This keeps datetime.now() from crashing and gives a
            # non-arbitrary time to fall back on.
            import rtc

            try:
                rtc.RTC().datetime = time_tuple = (
                        api_now.year, api_now.month, api_now.day,
                        api_now.hour, api_now.minute, api_now.second,
                        0, -1, -1
                )
            except Exception:
                pass

            return api_now

        except ValueError:
            return datetime.now()

    @staticmethod
    def parse_data(data: str) -> dict:
        """
        Loads the JSON data into a dictionary.

        :param data: the JSON data to load
        :return: the data dictionary
        """

        return loads(data)


class TransitAPI511(TransitAPI):
    """
    All the 511.org API calls are made from this class.
    """

    def __init__(self, requests: Session, api_key: str, format_: str):
        """
        Constructs a 'TransitApi' object with which to communicate with 511.org.

        :param requests: the requests object with which to contact the API
        :param api_key: the unique key given to the end user
        :param format_: the format (such as 'json' or 'xml') to return
        """

        self._api_key = api_key
        self._format = format_
        self._requests = requests

    def _get_command_url(self, command, parameters):
        """
        Generates the url with which to make the request.

        :param command: the path to use for the request
        :param parameters: the parameters to use for the request
        :return: the completed url
        """

        return f'https://{BASE_URL}/transit{command}?api_key={self._api_key}&{parameters}&format={self._format}'

    def get_data_handler(self) -> TransitDataHandler:
        """
        Gets the handler to parse the data returned from the API in the chosen format.

        :return: the data handler
        """

        if self._format == 'json':
            return _JsonHandler()
        else:
            raise ValueError(f'Invalid data format type {self._format}')

    def get_predictions(self, config: tuple[str, ...]) -> Response:
        """
        Makes a request for the predictions at a given stop.

        :param config: the config that has the predictions
        :return: the request response
        """

        command = '/StopMonitoring'
        agency = config[0]
        stop_code = config[1]
        parameters = f'agency={agency}&stopCode={stop_code}'
        endpoint = self._get_command_url(command, parameters)

        return self._requests.get(endpoint, timeout=10)
