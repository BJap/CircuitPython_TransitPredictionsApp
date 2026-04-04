"""
The default class for formatting transit predictions.
"""

# local
from transit.route import Route


class TransitPredictionFormatter:
    """
    Formats the transit predictions into text.
    """

    @staticmethod
    def format(route: Route, max_predictions: int, show_title: bool) -> list[str]:
        """
        Takes the route and formats its predictions for display.

        :param route: the route object for which to format into text
        :param max_predictions: the number of predictions to include
        :param show_title: whether to show the titles with the route
        :return: the formatted route text as a list of str
        """

        prediction_count = len(route.predictions)
        n = min(max_predictions, prediction_count)

        for i in range(n):
            route.predictions[i] = f'{route.predictions[i]}m'

        if route.predictions[0] == '0m':
            route.predictions[0] = 'Now'

        route_predictions = ' '.join(route.predictions[:n])

        if show_title:
            line_text = f'{route.route_code} {route.title}'

            return [line_text, route_predictions]
        else:
            return [f'{route.route_code} {route_predictions}']
