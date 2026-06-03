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

    # Cache credentials locally.
    _ssid = None
    _password = None

    @classmethod
    def connect(cls, ssid: str, password: str):
        """
        Connects to Wi-Fi using the provided credentials.

        :param ssid: the network for which to connect
        :param password: the network's password
        """

        cls._ssid = ssid
        cls._password = password

        if DEBUG_MODE:
            print(f'Connecting to WiFi using SSID: {ssid}')

        wifi.radio.connect(ssid, password)

        if DEBUG_MODE:
            print(f'Connected to WiFi at IP address: {wifi.radio.ipv4_address}\n')

    @classmethod
    def ensure_connected(cls):
        """
        Checks if the Wi-Fi connection is alive, and forces a reconnect if it dropped.
        """

        if not wifi.radio.connected and cls._ssid is not None:
            if DEBUG_MODE:
                print("Wi-Fi hardware link lost! Re-establishing connection...")

            wifi.radio.connect(cls._ssid, cls._password)

    @staticmethod
    def get_session() -> Session:
        """
        Gets and object with which to make requests.

        :return: the request-making object
        """

        pool = SocketPool(wifi.radio)

        return Session(pool, ssl.create_default_context())
