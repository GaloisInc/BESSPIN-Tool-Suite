
'''
Project: SSITH CyberPhysical Demonstrator
Name: outgauge.py
Author: Steven Osborn
Date: 26 August 2020

Implementation and datastructure for OutGauge support
(https://www.brunsware.de/insim/structOutGaugePack.html)

Listens to Outgauge from BeamNG on 127.0.0.1, port 4444
Unpacks the Outgauge struct and stores it.
'''

import socket

from .packet import OutGaugePacket
from .singleton import Singleton
from .component import ThreadExiting


class OutGauge(ThreadExiting):
    __metaclass__ = Singleton
    # socket parameters
    UDP_IP = "127.0.0.1"
    UDP_PORT = 4444
    BUFFER_SIZE = 1000

    def __init__(self):
        super().__init__(name="outgauge")
        self._last_packet = None

        # create a socket
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self.UDP_IP, self.UDP_PORT))

    def update(self):
        return self._last_packet

    def on_exit(self) -> None:
        self._sock.close()

    def on_poll(self, t) -> None:
        super().on_poll(t)
        data = self._sock.recv(self.BUFFER_SIZE)
        self._last_packet = OutGaugePacket.from_struct(data)


class OutGaugeCanBridge(ThreadExiting):
    def __init__(self):
        super().__init__()
        self._og = OutGauge()

    def on_poll(self, t) -> None:
        super().on_poll(t)
        self._og = self._og.update()
