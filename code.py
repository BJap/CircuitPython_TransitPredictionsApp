"""
This class is used to run apps on a sbc controller.

Suggested safety for when there is an issue with the network
https://learn.adafruit.com/pico-w-wifi-with-circuitpython
"""

from microcontroller import reset
from os import getenv
from time import sleep

# local
from network import Wifi
from transit_predictions_app import TransitPredictionsApp

RESET_DELAY_SEC = 30
RUN_DELAY_SEC = 5

try:
    # Sometimes while coding things can hang up so good to leave a gap of time to wait
    # before running the app as a way to bail out and get the IDE To connect and fix it.
    sleep(RUN_DELAY_SEC)

    Wifi.connect(
        getenv('CIRCUITPY_WIFI_SSID'),
        getenv('CIRCUITPY_WIFI_PASSWORD')
    )

    requests = Wifi.get_session()

    app = TransitPredictionsApp(requests)
    app.run()
except Exception as e:
    print(f'Error:\n {str(e)}')
    print(f'Resetting microcontroller in {RESET_DELAY_SEC} seconds')
    # Comment out these if doing active development in case of failure to the program ends
    sleep(RESET_DELAY_SEC)
    reset()
