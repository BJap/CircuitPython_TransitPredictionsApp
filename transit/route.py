"""
Holder for the route information and predictions.
"""


class Route:
    """
    A data class for a route.
    """

    def __init__(self, route_code: str, title: str):
        """
        Constructs a 'Route' object including an empty predictions list.

        :param route_code: the code the represents the route
        :param title: the title of the route
        """

        self.route_code = route_code
        self.title = title
        self.predictions: [int] = []

    def add_prediction(self, minutes: int):
        """
        Adds a prediction to the route.

        :param minutes: the number of minutes for the predicted transit to arrive
        """

        self.predictions.append(minutes)
