"""
From example:
https://learn.adafruit.com/pico-w-wifi-with-circuitpython/pico-w-basic-wifi-test
"""

from socketpool import SocketPool
import ssl
import wifi

# lib
import adafruit_requests as requests


class Wifi:
    """
    Allows the device to connect to the internet using Wi-Fi
    """

    @staticmethod
    def connect(ssid, password):
        """
        Connects to Wi-Fi using the provided credentials.

        :param ssid: the network for which to connect
        :param password: the network's password
        """

        print(f'Connecting to WiFi using SSID: {ssid}')

        wifi.radio.connect(ssid, password)

        print(f'Connected to WiFi at IP address: {wifi.radio.ipv4_address}\n')

    @staticmethod
    def get_session():
        """
        Gets and object with which to make requests.

        :return: the request-making object
        """

        pool = SocketPool(wifi.radio)

        return requests.Session(pool, ssl.create_default_context())
