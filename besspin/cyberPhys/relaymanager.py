#! /usr/bin/env python3
from besspin.base.utils.misc import *
import besspin.cyberPhys.cyberphyslib.cyberphyslib.demonstrator.component as ccomp

import time
import serial, serial.tools.list_ports_posix

class RelayManager(ccomp.Component):
    """ 
    Controls USB relay Amazon ASIN B01CN7E0RQ that is a part of cyberphys admin PC
    It resets the Teensy board
    """
    ## Relay interface and control parameters
    # Relays here are Amazon ASIN B01CN7E0RQ
    relay_usb_product_id = "29987"  # note, this is a USB product ID, not a process ID
    relay_baud = 9600
    relay_on = b'\xA0\x01\x01\xA2'
    relay_off = b'\xA0\x01\x00\xA1'
    relay_delay = 0.5

    def __init__(self, *args):
        super(RelayManager, self).__init__(*args)

    @staticmethod
    def iterate_relays():
        """iterator to fetch all usb relays"""
        # get all connected serial devices
        usb_devices = list(serial.tools.list_ports_posix.comports())

        for usb_device in usb_devices:
            if RelayManager.relay_usb_product_id in str(usb_device.pid):

                usb_relay = serial.Serial(port=usb_device.device,
                                          baudrate=RelayManager.relay_baud,
                                          timeout=0.5)
                yield usb_relay

    @staticmethod
    def turn_on_relays() -> None:
        """turn on all led manager relays"""
        for relay in RelayManager.iterate_relays():
            relay.flushInput()
            relay.write(RelayManager.relay_on)

    @staticmethod
    def turn_off_relays() -> None:
        """turn off all led manager relays"""
        for relay in RelayManager.iterate_relays():
            relay.flushInput()
            relay.write(RelayManager.relay_off)


    @recv_topic("base-topic","RESET 0")
    def _(self, t):
        """a topic level callback"""
        printAndLog(f"{self.name} Reset requested")
        self.turn_on_relays()
        time.sleep(self.relay_delay)
        self.turn_off_relays()
        self.send_message(ccomp.Message(f"READY 0"), getSetting('cyberPhysComponentBaseTopic'))
