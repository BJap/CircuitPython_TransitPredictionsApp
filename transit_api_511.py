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

# libs
from adafruit_datetime import datetime

BASE_URL = 'api.511.org'


class JsonHandler:
    """
    Parses the data returned in JSON format from the 511.org API.
    """

    @staticmethod
    def parse_data(data):
        """
        Takes the cleartext response data from an API call and formats it to a JSON map

        :return: the data in JSON format
        """

        return loads(data)

    @staticmethod
    def predictions_for_route_codes(json, route_codes, direction):
        """
        Takes all the prediction JSON and collects only the relevant items.

        :param json: the data to parse
        :param route_codes: the routes of interest
        :param direction: the direction of interest
        :return: the predictions that are available if any
        """

        predictions = {}

        # The time the predictions data was sent
        # This is used because some predictions come back with a 'created' unix time stamp
        # of 0, so they are inaccurate to use for temporal subtraction so a unified baseline
        # of 'now' is used to get around this flaw in the API response
        data_time = json['ServiceDelivery']['StopMonitoringDelivery']['ResponseTimestamp']
        # CircuitPython only parses DateTime from iso formats without the 'T' and 'Z' in them.
        data_time = data_time.replace('T', ' ').replace('Z', '')
        now = datetime.fromisoformat(data_time)

        # The list of upcoming visits to the stop in the predictions
        visits = json['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']

        # Iterate over all the upcoming visits and gather predictions
        for visit in visits:
            trip = visit['MonitoredVehicleJourney']
            route_code = trip['LineRef']

            # If the route code is of interest in the trip in the correct direction
            if route_code in route_codes and trip['DirectionRef'] == direction:
                # If predictions doesn't have the route in it yet, add it
                if route_code not in predictions:
                    title = trip['PublishedLineName']
                    route = Route(route_code, title)
                    predictions[route_code] = route

                # The predicted time of the visit
                prediction_info = trip['MonitoredCall']
                arrival_time = prediction_info['ExpectedArrivalTime']
                # CircuitPython only parses DateTime from iso formats without the 'T' and 'Z' in them.
                arrival_time = arrival_time.replace('T', ' ').replace('Z', '')
                prediction = datetime.fromisoformat(arrival_time)

                # The minutes until the trip's arrival
                minutes = int((prediction - now).seconds / 60)

                # Add the minutes to the set of predictions
                predictions[route_code].add_prediction(minutes)

        # Return the predictions for the desired route codes
        return predictions

    @staticmethod
    def prediction_seconds_soonest(json, route_codes, direction):
        """
        Determines when the next transit will arrive.

        :param json: the data to parse
        :param route_codes: the routes of interest
        :param direction: the direction of interest
        :return: the next arrival time or 0 if there are no predictions
        """

        # The time the predictions data was sent
        data_time = json['ServiceDelivery']['StopMonitoringDelivery']['ResponseTimestamp']
        # CircuitPython only parses DateTime from iso formats without the 'T' and 'Z' in them.
        data_time = data_time.replace('T', ' ').replace('Z', '')
        now = datetime.fromisoformat(data_time)

        # The list of upcoming visits to the stop in the predictions
        visits = json['ServiceDelivery']['StopMonitoringDelivery']['MonitoredStopVisit']

        # Iterate over all the upcoming visits and find the soonest arrival of desired route codes
        for visit in visits:
            trip = visit['MonitoredVehicleJourney']
            route_code = trip['LineRef']

            # If the route code is of interest in the trip in the correct direction
            if route_code in route_codes and trip['DirectionRef'] == direction:
                # The predicted time of the visit
                prediction_info = trip['MonitoredCall']
                arrival_time = prediction_info['ExpectedArrivalTime']
                # CircuitPython only parses DateTime from iso formats without the 'T' and 'Z' in them.
                arrival_time = arrival_time.replace('T', ' ').replace('Z', '')
                prediction = datetime.fromisoformat(arrival_time)

                # Return how many seconds until the next arrival
                return int((prediction - now).seconds)

        # There are no predictions of interest, return None
        return None


class Route:
    """
    A data class for a route.
    """

    def __init__(self, route_code, title):
        """
        Constructs a 'Route' object including an empty predictions list.

        :param route_code: the code the represents the route
        :param title: the title of the route
        """

        self.route_code = route_code
        self.title = title
        self.predictions = []

    def add_prediction(self, minutes):
        """
        Adds a prediction to the route.

        :param minutes: the number of minutes for the predicted transit to arrive
        """

        self.predictions.append(minutes)


class TransitApi:
    """
    All the 511.org API calls are made from this class.
    """

    def __init__(self, requests, api_key, r_format):
        """
        Constructs a 'TransitApi' object with which to communicate with 511.org.

        :param requests: the requests object with which to contact the API
        :param api_key: the unique key given to the end user
        :param r_format: the format (such as 'json' or 'xml') to return
        """

        self.__api_key = api_key
        self.__r_format = r_format
        self.__requests = requests

    def __get_command_url(self, command, parameters):
        """
        Generates the url with which to make the request.

        :param command: the path to use for the request
        :param parameters: the parameters to use for the request
        :return: the completed url
        """

        return f'https://{BASE_URL}/transit{command}?api_key={self.__api_key}&{parameters}&format={self.__r_format}'

    def get_data_handler(self):
        """
        Gets the handler to parse the data returned from the API in the chosen format.

        :return: the data handler
        """

        if self.__r_format == 'json':
            return JsonHandler()
        else:
            return None

    def predictions_for_stop_code(self, agency, stop_code):
        """
        Makes a request for the predictions at a given stop.

        :param agency: the agency that has the predictions
        :param stop_code: the stop for which to gather predictions
        :return: the request response
        """

        command = '/StopMonitoring'
        parameters = f'agency={agency}&stopCode={stop_code}'
        endpoint = self.__get_command_url(command, parameters)

        return self.__requests.get(endpoint)
