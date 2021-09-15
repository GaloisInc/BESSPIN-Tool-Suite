import serial
import re

from .component import ComponentPoller, ComponentStatus
from cyberphyslib.demonstrator.logger import teensy_logger

class TeensyMonitor(ComponentPoller):
    """
    Teensy serial reader
    """
    # Serial port setup
    READ_LIMIT = 254
    THROTTLE_MAX = 926
    THROTTLE_MIN = 64
    THROTTLE_GAIN =  100
    BRAKE_MAX = 270
    BRAKE_MIN = 50
    BRAKE_GAIN = 100
    COM_PORT = 'COM43'
    BAUDRATE = 115200

    gear = 0
    brake_raw = 0
    brake = 0
    throttle_raw = 0
    throttle = 0

    def __init__(self):
        super().__init__("teensy", [],[],sample_frequency= 20.0)
        
        # Teensy related variables
        self.re_gear = re.compile('shifter_gear: 0X\d*')
        self.re_brake = re.compile('brake_raw: \d*')
        self.re_throttle = re.compile('throttle_raw: \d*')

    def on_start(self):
        """open serial port"""
        self.teensy_serial = serial.Serial(self.COM_PORT, self.BAUDRATE, timeout=0)
        self.start_poller()

    def on_poll_poll(self, t):
        """read and partse serial data"""
        try:
            val = self.teensy_serial.read(self.READ_LIMIT).decode('utf-8')
            gear_raw = self.re_gear.findall(val)
            if gear_raw:
                gear_raw = int(gear_raw[-1].split()[-1],16)
                #            'P'     'R'         'N'   'D'
                gear_map = {0x28: 1, 0x27: -1, 0x26: 0, 0x25: 2}
                self.gear = gear_map.get(val, 0)

            throttle_raw = self.re_throttle.findall(val)
            if throttle_raw:
                self.throttle_raw = int(throttle_raw[-1].split()[-1])
                # Scale the throttle
                tmp_throttle = max(self.throttle_raw - self.THROTTLE_MIN, 0)
                tmp_throttle = tmp_throttle * self.THROTTLE_GAIN / (self.THROTTLE_MAX - self.THROTTLE_MIN)
                self.throttle = min(max(tmp_throttle, 0), 100)/100

            brake_raw = self.re_brake.findall(val)
            if brake_raw:
                self.brake_raw = int(brake_raw[-1].split()[-1])
                # Scale the brake
                tmp_brake = max(self.BRAKE_MAX - self.brake_raw, 0)
                tmp_brake = tmp_brake * self.BRAKE_GAIN / (self.BRAKE_MAX - self.BRAKE_MIN)
                self.brake = min(max(tmp_brake, 0), 100)/100

            # TODO: remove this from the log?
            teensy_logger.info(f"Brake: {self.brake}, Throttle: {self.throttle}, Gear: {self.gear}")
            self.teensy_serial.reset_input_buffer()
        except Exception as exc:
            teensy_logger.warning(f"Serial port exception: {exc}")  

    @property
    def is_healthy(self):
        """is teensy functioning properly?"""
        if self.brake_raw == 0 or self.throttle_raw == 0:
            return False
        else:
            return True
