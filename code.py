"""
This file is used to run apps on a sbc controller.

Suggested safety for when there is an issue with the network
https://learn.adafruit.com/pico-w-wifi-with-circuitpython
"""

from microcontroller import reset
from os import getenv
from time import sleep

# local
from config import DEBUG_MODE
from app511.predictions_app_511 import TransitPredictionsApp511
from display.configuration_console import ConfigurationConsole
from display.configuration_matrix_64_x_32_fancy import ConfigurationMatrix64X32Fancy
from network import Wifi

RESET_DELAY_SEC = 30
RUN_DELAY_SEC = 0

try:
    # Sometimes while coding things can hang up so good to leave a gap of time to wait
    # before running the app as a way to bail out and get the IDE To connect and fix it.
    sleep(RUN_DELAY_SEC)

    Wifi.connect(
        getenv('CIRCUITPY_WIFI_SSID'),
        getenv('CIRCUITPY_WIFI_PASSWORD')
    )

    requests = Wifi.get_session()

    if DEBUG_MODE:
        display_config = ConfigurationConsole()
    else:
        display_config = ConfigurationMatrix64X32Fancy()

    app = TransitPredictionsApp511(requests, display_config)

    while True:
        wait = app.update()

        if DEBUG_MODE:
            print(f'Refreshing predictions in {wait} seconds\n')

        sleep(wait)
except Exception as e:
    if DEBUG_MODE:
        print(f'Error:\n {str(e)}')
        print(f'Resetting microcontroller in {RESET_DELAY_SEC} seconds')
    # Comment out these if doing active development in case of failure to the program ends.
    sleep(RESET_DELAY_SEC)
    reset()
