"""
Project: SSITH CyberPhysical Demonstrator
Name: speedometer.py
Author: Kristofer Dobelstein, Ethan Lew
Date: 20 November 2020
Python: 3.8.3
O/S: Windows 10
This routine is a bridge between BeamNG's electrics sensor and a teensy board
that controls the Smart ForTwo instrument cluster. It provides the following
functionality:
1. Receives the BeamNG sensor data
2. Sends
        * speed
        * fuel
        * throttle
        * gear
        * oil
        * parkingbrake
        * highbeam
        * headlights
        * right signal
        * left signal
        * esc active
        * abs active
        * brake lights
    to the teensy board.
"""
import struct
import serial
import serial.tools.list_ports
from time import sleep
from .component import ComponentPoller
import cyberphyslib.demonstrator.config as config
from .logger import speedo_logger

# Calibration constant that converts meters per second to mph
METER_PER_SEC_TO_MPH = 2.23694

# infer boolean value from real valued sensor in [0, 1]
BOOL_THRESH = 0.5

# Outgage recieve buffer size.  This just needs to be big enough to handle
# the max packet size.
BUFFER_SIZE = 100
SERIAL_BAUD_RATE = 38400
SERIAL_TIMEOUT = 0.5


def char(x: int) -> int:
    """ensures that int x is inside char range"""
    assert isinstance(x, int)
    return max(min(x, 127), -128)


def uchar(x: int) -> int:
    """ensures that int is inside uchar range"""
    assert isinstance(x, int)
    return max(min(x, 255), 0)


class Speedo(ComponentPoller):
    """Speedometer Service of Smart Fortwo Instrument Cluster"""
    gear_map = {"P": 	-2,
                "R": 	-1,
                "N": 	0,
                "D": 	0xA,
                "1": 	1,
                "2": 	2,
                "3": 	3,
                "4": 	4,
                "5": 	5,
                "S1" : 1,
                "M1" : 2}

    def __init__(self):
        super().__init__("speedo", [config.BEAMNG_COMPONENT_SENSORS], [], sample_frequency=60.0)
        self._send_types = (*((float,) * 3), char, *((uchar,) * 4), *((bool,) * 5))
        self._sensor_electrics = None
        self._teensy_ser = None
        self.setup_serial()

    def on_start(self):
        speedo_logger.info("Starting speedometer thread.")
        self.start_poller()

    def setup_serial(self):
        """find teensy and create a serial session"""
        # scan active serial ports to find where the first Arduino Micro is
        # attached since this is a fixed system, we know there's only one
        # present
        speedometer_com_port = None
        com_ports = list(serial.tools.list_ports.comports())

        for p in com_ports:
            if "USB Serial Device" in p.description:
                speedometer_com_port = str(p.device)

        if not speedometer_com_port:
            speedo_logger.error('USB speedometer not found.')
            return

        # try to create a serial port object for the interface with the
        # Arduino-based speedometer instrument cluster
        try:
            self._teensy_ser = serial.Serial(port=speedometer_com_port,
                                             baudrate=SERIAL_BAUD_RATE,
                                             timeout=SERIAL_TIMEOUT)
            self._teensy_ser.flushInput()
            sleep(1)
        # if no speedometer, print an error to the console and exit the script.
        except:
            speedo_logger.error(f'Unable to connect to USB speedometer via'
                         f'{speedometer_com_port}.')

    def on_poll_poll(self, t):
        """collect relevant electrics data and send to teensy"""
        if self._sensor_electrics is not None:
            gear = self.gear_map.get(self._sensor_electrics['gear'], self._sensor_electrics['gear'])
            to_send = [self._sensor_electrics["wheelspeed"] * METER_PER_SEC_TO_MPH, # float
                       self._sensor_electrics["fuel"], # float
                       self._sensor_electrics["throttle"], # float
                       gear, # char
                       self._sensor_electrics["oil"], # unsigned char
                       1 if self._sensor_electrics["parkingbrake"] > BOOL_THRESH else 0, # unsigned char
                       self._sensor_electrics["highbeam"], # unsigned char
                       self._sensor_electrics["headlights"], # unsigned char
                       True if self._sensor_electrics["right_signal"] > BOOL_THRESH else False, # bool
                       True if self._sensor_electrics["left_signal"] > BOOL_THRESH else False, # bool
                       self._sensor_electrics["esc_active"], # bool
                       self._sensor_electrics["abs_active"], # bool
                       self._sensor_electrics["brake_lights"] # bool
                       ]
            for idx, (t, v) in enumerate(zip(self._send_types, to_send)):
                try:
                    to_send[idx] = t(v)
                except:
                    speedo_logger.error(f"Speedometer cannot send at index {idx}, having value {v}, but requiring type {t}")
                    return
            out_bytes = struct.pack("3fb4B5?", *to_send)
            if self._teensy_ser is not None:
                self._teensy_ser.write(out_bytes)

    def on_exit(self) -> None:
        self.stop_poller()
        del self._teensy_ser

    @recv_topic("beamng-sensors")
    def _(self, msg, t):
        """subscribe to sim service sensor electrics"""
        self._sensor_electrics = msg._msg