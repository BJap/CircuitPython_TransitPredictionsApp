"""
All the functionality needed to interact with the 511.org API and parse the data is here.

API reference:
https://511.org/open-data/transit

Current reference:
https://511.org/sites/default/files/2022-11/511%20SF%20Bay%20Open%20Data%20Specification%20-%20Transit.pdf

In order to obtain an access token to use for this API go to:
https://511.org/open-data/token
"""

from gc import collect
from json import loads
from zlib import decompress

# libs
from adafruit_datetime import datetime

BASE_URL = 'api.511.org'

DEFAULT_PREDICTIONS = 2

ERROR_REFRESH_SEC = 30
MAX_REFRESH_SEC = 60
MIN_REFRESH_SEC = 10


class JsonHandler:
    """
    Parses the data returned in JSON format from the 511.org API.
    """

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

        # There are no predictions of interest, return 0 seconds until the next arrival
        return 0


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

    def __init__(self, requests, api_key):
        """
        Constructs a 'TransitApi' object with which to communicate with 511.org.

        :param requests: the requests object with which to contact the API
        :param api_key: the unique key given to the end user
        """

        self.__api_key = api_key
        self.__requests = requests

    def __get_command_url(self, command, parameters):
        """
        Generates the url with which to make the request.

        :param command: the path to use for the request
        :param parameters: the parameters to use for the request
        :return: the completed url
        """
        
        return f'https://{BASE_URL}/transit{command}?api_key={self.__api_key}&{parameters}&format=json'

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


class TransitPredictions511:
    """
    A class for the TransitPredictionsApp to use for its source data.
    """

    def __init__(
            self,
            requests,
            api_key,
            agency,
            stop_code,
            route_codes,
            direction,
            max_predictions=DEFAULT_PREDICTIONS
    ):
        """
        Constructs a predictions object to feed data to the TransitPredictionsApp.

        :param requests: the requests object with which to contact the API
        :param api_key: the unique key given to the end user
        :param agency: the agency that has the predictions
        :param stop_code: the stop for which to gather predictions
        :param route_codes: the routes of interest
        :param direction: the direction of interest
        :param max_predictions: the maximum predictions to get per route
        """

        self.__agency = agency
        self.__api = TransitApi(requests, api_key)
        self.__direction = direction
        self.__max_predictions = max_predictions
        self.__route_codes = route_codes
        self.__stop_code = stop_code

    @staticmethod
    def check_for_success(status_code):
        """
        Checks the response for a success.

        :param status_code: the status code to check
        :return: whether the status code indicates a success
        """

        return 200 <= status_code < 300

    def __poll(self):
        """
        Polls for prediction data and stores it at class level.
        """

        # Wipe the existing data and fetch new data
        self.__data = None
        response = self.__api.predictions_for_stop_code(self.__agency, self.__stop_code)
        self.__status_code = response.status_code
        self.__reason = response.reason.decode('utf-8')

        if self.check_for_success(self.__status_code):
            # There's a bug for this that was fixed in
            # https://github.com/adafruit/circuitpython/pull/8335
            # Then this will probably become:
            # data = decompress(response.content, 31).decode('utf-8')
            data = decompress(response.content[10:], -31)[3:].decode('utf-8')
            self.__data = loads(data)
        else:
            print(f'Status code: {self.__status_code}\n')
            print(f'Reason: {self.__reason}\n')

        response.close()

        # Free up all this memory or the next poll's allocation will fail on some devices
        del response
        del data
        collect()

    def get_predictions(self):
        """
        Gets the predictions for the PredictionsApp.

        :return: the lines of text to display in format of:
            - <route code> <route title>
            - <prediction 1> <prediction 2> ...
        """

        print(f'Getting predictions for agency {self.__agency} for stop_code {self.__stop_code}')

        self.__poll()
        
        # Polling failed
        if not self.__data:
            return ['Network Error', f'{self.__status_code}', f'{self.__reason}']

        predictions = JsonHandler.predictions_for_route_codes(self.__data, self.__route_codes, self.__direction)
        prediction_text = []

        if predictions:
            for route_code in self.__route_codes:
                if route_code in predictions:
                    route = predictions[route_code]

                    prediction_text.append(f'{route_code} {route.title}')

                    prediction_count = len(route.predictions)
                    n = min(self.__max_predictions, prediction_count)

                    for i in range(n):
                        route.predictions[i] = f'{route.predictions[i]}m'

                    if route.predictions[0] == '0m':
                        route.predictions[0] = 'Now'

                    route_predictions = ' '.join(route.predictions[:n])

                    prediction_text.append(route_predictions)
        
        if prediction_text:
            for text in prediction_text:
                print(text)
                
            print('')
        else:
            print('No predictions available\n')

        return prediction_text

    def get_refresh_interval(self):
        """
        Get when the next refresh of prediction data should occur.

        :return: the minimum time, the time until the next transit arrives, or the maximum time
        """
        
        # Polling failed
        if not self.__data:
            return ERROR_REFRESH_SEC

        seconds_soonest = int(JsonHandler.prediction_seconds_soonest(self.__data, self.__route_codes, self.__direction))
        
        print(f'The next desired transit option arrives in {seconds_soonest} seconds\n')

        return max(min(seconds_soonest, MAX_REFRESH_SEC), MIN_REFRESH_SEC)
