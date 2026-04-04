"""
From example:
https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-basic-wifi-test
"""

from socketpool import SocketPool
import ssl
import wifi

# lib
from adafruit_requests import Session

# local
from config import DEBUG_MODE


class Wifi:
    """
    Allows the device to connect to the internet using Wi-Fi
    """

    @staticmethod
    def connect(ssid: str, password: str):
        """
        Connects to Wi-Fi using the provided credentials.

        :param ssid: the network for which to connect
        :param password: the network's password
        """

        if DEBUG_MODE:
            print(f'Connecting to WiFi using SSID: {ssid}')

        wifi.radio.connect(ssid, password)

        if DEBUG_MODE:
            print(f'Connected to WiFi at IP address: {wifi.radio.ipv4_address}\n')

    @staticmethod
    def get_session() -> Session:
        """
        Gets and object with which to make requests.

        :return: the request-making object
        """

        pool = SocketPool(wifi.radio)

        return Session(pool, ssl.create_default_context())
