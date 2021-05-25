"""
Project: SSITH CyberPhysical Demonstrator
leds_manage.py
Author: Kristofer Dobelstein <kris.dobelstein@agilehardwarenwllc.com>, Ethan Lew <elew@galois.com>
Date: 03/03/2021
Python 3.8.3
O/S: Windows 10

Component to manage the LED fixture

TODO: fadecandy server launch and management
"""
import typing as typ
import opclib.opc as opc
import time
import pandas as pd
import numpy as np
import enum
import serial, serial.tools.list_ports_windows
import pathlib
import os
import subprocess
import psutil

from .component import ComponentPoller, ComponentStatus
from .logger import led_manage_logger
from .message import Message
from cyberphyslib.demonstrator.leds import LedString
import cyberphyslib.demonstrator.leds as cled
import cyberphyslib.demonstrator.config as cconf


class LedPatterns(enum.IntEnum):
    """Led pattern names defined by cyberphys spec"""
    NOMINAL = enum.auto()
    SSITH = enum.auto()
    STEERING_HACK = enum.auto()
    TRANSMISSION_HACK = enum.auto()
    THROTTLE_HACK = enum.auto()
    BRAKE_HACK = enum.auto()
    ALL_OFF = enum.auto()
    ALL_ON = enum.auto()


# how the patterns are referenced in the csv encoding
led_pattern_csv_names = {
    "nominal pattern": LedPatterns.NOMINAL,
    "ssith pattern": LedPatterns.SSITH,
    "steering hack pattern": LedPatterns.STEERING_HACK,
    "transmission hack pattern": LedPatterns.TRANSMISSION_HACK,
    "throttle hack pattern": LedPatterns.THROTTLE_HACK,
    "brake hack pattern": LedPatterns.BRAKE_HACK,
    "all off": LedPatterns.ALL_OFF,
    "all on": LedPatterns.ALL_ON
}


class LedManagerStatus(enum.IntEnum):
    READY = enum.auto()
    ERROR = enum.auto()


class LedManagerComponent(ComponentPoller):
    """TODO: LedManager description"""
    ## Relay interface and control parameters
    # Relays here are Amazon ASIN B01CN7E0RQ
    relay_usb_product_id = "29987"  # note, this is a USB product ID, not a process ID
    relay_baud = 9600
    relay_on = b'\xA0\x01\x01\xA2'
    relay_off = b'\xA0\x01\x00\xA1'

    # LED network refresh time
    regular_update_rate = 0.033  # seconds between updates
    hack_update_rate = 0.0165  # seconds between updates

    # Power management timing constants
    system_time_delay_short = 1  # seconds
    system_time_delay_warmup = 15  # seconds
    relay_time_delay_blip = 0.1  # seconds
    relay_time_delay_short = 0.25  # seconds
    relay_time_delay_medium = 1  # seconds
    relay_time_delay_long = 2  # seconds

    # address of open pixel control client
    opc_address = 'localhost:7890'

    @staticmethod
    def iterate_relays():
        """iterator to fetch all usb relays"""
        # get all connected serial devices
        usb_devices = list(serial.tools.list_ports_windows.comports())

        for usb_device in usb_devices:
            if LedManagerComponent.relay_usb_product_id in str(usb_device.pid):

                usb_relay = serial.Serial(port=usb_device.device,
                                          baudrate=LedManagerComponent.relay_baud,
                                          timeout=0.5)
                yield usb_relay

    @staticmethod
    def turn_on_relays(relay_pause: float = 4.0) -> None:
        """turn on all led manager relays"""
        for relay in LedManagerComponent.iterate_relays():
            led_manage_logger.info("Turn on USB relay at " + str(relay.port))
            relay.flushInput()
            relay.write(LedManagerComponent.relay_on)
            #time.sleep(relay_pause) # NOTE: needed?

    @staticmethod
    def turn_off_relays() -> None:
        """turn off all led manager relays"""
        for relay in LedManagerComponent.iterate_relays():
            led_manage_logger.info("Turn off USB relay at " + str(relay.port))
            relay.flushInput()
            relay.write(LedManagerComponent.relay_off)

    @classmethod
    def from_csv(cls, csv_fname: str):
        # csv hack names
        hack_names = led_pattern_csv_names.keys()

        # read csv and load led strings from row descriptions
        ledf = pd.read_csv(csv_fname)
        led_strs = []
        for idx, row in ledf.iterrows():
            hd = {}
            for hack_name in hack_names:
                pat, color = row[hack_name], eval(row[hack_name + " color"])
                assert len(color) == 3, f"colors must have 3 elements (found {color})"

                # match pattern key to pattern object
                if pat == "off":
                    pattern = cled.ConstantPattern((0, 0, 0))
                elif pat == "on":
                    pattern = cled.ConstantPattern(color)
                elif pat == "ants":
                    pattern = cled.AntsPattern(color, 4, False)
                elif pat == "ants_reverse":
                    pattern = cled.AntsPattern(color, 4, True)
                elif pat == "pulse":
                    pattern = cled.PulsePattern(color, 1.0, 10, 10)
                else:
                    raise ValueError(f"invalid pattern {pat}")

                hd[led_pattern_csv_names[hack_name]] = pattern
            led_strs += [cled.LedString(row["name"], hd, LedPatterns.NOMINAL, row["length"])]
        return cls(led_strs)

    @classmethod
    def for_ignition(cls):
        led_string_filepath = pathlib.Path(os.path.realpath(__file__)).parent / "utils" / \
                           "led_strings_comprehensive_tuple_colors.csv"
        return cls.from_csv(led_string_filepath)

    def __init__(self, led_strings: typ.Sequence[LedString]):
        super().__init__("ledm", [(cconf.DIRECTOR_PORT, "ledm-commands")],
                         [(cconf.LED_MANAGE_PORT, "ledm-events")],
                         sample_frequency=1 / self.regular_update_rate)
        self.client = opc.Client(self.opc_address)
        self.led_strings = led_strings
        self._no_client = False

    def prepare_call(self):
        """prepare process call for fadecandy server OPC"""
        base_path = pathlib.Path(os.path.realpath(__file__)).parent / "utils"
        fadecandy_executable = "fcserver.exe"
        fadecandy_json_cfg = "cyberphys_led_strings.json"
        return [str((base_path / fadecandy_executable).resolve()),
                str((base_path / fadecandy_json_cfg).resolve())]

    def start_opc(self):
        """starts the fadecandy server OPC server"""
        call = self.prepare_call()
        led_manage_logger.debug(f'Starting Fadecandy PC Server process: {call}')
        self.process = subprocess.Popen(call)

    def kill_opc(self):
        """kill the fadecandy server OPC process"""
        # check if Fadecandy server is running
        fadecandy_pid = None
        for process in psutil.process_iter():
            try:
                if 'fcserver' in process.name():
                    print("Fadecandy server is running as pid " + str(process.pid))
                    fadecandy_pid = process.pid
            except:
                pass
        # if it is running, shut it down and restart
        if fadecandy_pid is not None:
           print("Shutting down Fadecandy and opening in known configuration.")
           os.kill(fadecandy_pid, 9)

    def system_startup(self):
        """system startup procedure required to turn on LEDs without persistent pixels"""

        # check whether we can connect to the OPC server
        if not self.client.can_connect():
            # error has occurred
            self.send_message(Message(LedManagerStatus.ERROR), "ledm-events")
            self._no_client = True
            return
        # TODO: check that the number of relays is correct?

        # turn off all relays
        self.turn_off_relays()

        self.update_pattern(LedPatterns.ALL_OFF)

        # turn off all LEDs
        # Command all LED strings to turn on
        self.update_leds()

        # let the system stabilize
        time.sleep(self.system_time_delay_short)

        self.update_pattern(LedPatterns.ALL_ON)

        # Send the list of on tuples to the client
        self.update_leds()

        # rest for a moment
        time.sleep(self.system_time_delay_short)

        # turn on all relays and let LEDs warm up
        self.turn_on_relays(self.system_time_delay_short)
        time.sleep(self.system_time_delay_warmup)

        # now quickly power cycle the system and let it run
        self.turn_off_relays()
        time.sleep(self.system_time_delay_short)
        self.turn_on_relays(self.relay_time_delay_short)

        self.send_message(Message(LedManagerStatus.READY), "ledm-events")

    def test_device(self):
        """call this to test the device -- requires a running server"""
        self.system_startup()
        self.update_pattern(LedPatterns.NOMINAL)

        # Send the list of on tuples to the client
        self.update_leds()

        while True:
            time.sleep(self.regular_update_rate)
            for ls in self.led_strings:
                ls.update()
            self.update_leds()

    def update_leds(self):
        """update pixels to values inside led strings"""
        self.client.put_pixels(self.pixel_array.tolist())

    def update_pattern(self, pattern_name):
        """update the pattern to display"""
        for ls in self.led_strings:
            ls.update_pattern(pattern_name)

    @property
    def pixel_array(self):
        return np.concatenate([l.pixel_array for l in self.led_strings])

    def wait_ready_command(self):
        while not self._start_finished and not self._no_client:
            time.sleep(0.5)
        return ComponentStatus.READY if not self._no_client else ComponentStatus.ERROR

### component relevant methods
    def on_start(self):
        self.start_opc()
        self.system_startup()
        self.update_pattern(LedPatterns.NOMINAL)
        self.update_leds()
        self.start_poller()

    def on_exit(self):
        self.kill_opc()

    def on_poll_poll(self, t):
        """LED Manager Component Mainloop"""
        for ls in self.led_strings:
            ls.update()
        self.update_leds()

    @recv_topic("pattern-request")
    def _(self, msg, t):
        """subscribe to requests to change the led pattern"""
        self.update_pattern(msg.message)
        self.update_leds()
