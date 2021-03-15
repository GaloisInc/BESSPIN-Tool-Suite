"""
Project: SSITH CyberPhysical Demonstrator
Name: logging.py
Author: Steven Osborn <steven@lolsborn.com>, Ethan Lew <elew@galois.com>
Date: 01 January 2021

Packet Definitions
NOTE: OutGaugePacket was separated from outgauge as the Singleton object causes the
OutGauge class to bind to sockets without even being instantiated by the user. This
is problematic when testing with other sockets.
"""
import struct


class OutGaugePacket:
    fields = ["time",
              "car",
              "flags",
              "gear",
              "plid",
              "speed",
              "rpm",
              "turbo",
              "engtemp",
              "fuel",
              "oilpressure",
              "oiltemp",
              "dashlights",
              "showlights",
              "throttle",
              "brake",
              "clutch",
              "display1",
              "display2",
              "optional_id"]

    fmt_str = 'I4sH2c7f2I3f16s16si'

    @classmethod
    def from_beamng(cls, sensor_electrics):
        """packet from BeamNG electrics data"""
        # default values as not all values are meaningful
        default_data = [0, b'beam', 49152, b'\x03', b'\x00', 29.002765655517578, 6482.79736328125, 0.0, 88.43984985351562,
                        0.9980279207229614, 0.0, 84.8863754272461, 1910, 0, 0.9660662412643433, 0.0, 0.0,
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00',
                        b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00', 0]
        packet = cls(default_data)
        packet.speed = sensor_electrics['wheelspeed']
        packet.rpm = sensor_electrics['rpm']
        packet.fuel = sensor_electrics['fuel']
        packet.oiltemp = sensor_electrics['oil_temperature']
        packet.engtemp = sensor_electrics['water_temperature']
        packet.throttle = sensor_electrics['throttle_input']
        # gear is signed
        packet.gear = struct.pack("b", sensor_electrics['gear'])
        packet.brake = sensor_electrics['brake_input']
        packet.clutch = sensor_electrics['clutch']
        return packet

    @classmethod
    def from_struct(cls, data):
        """from bytearray"""
        outgauge_pack = struct.unpack(cls.fmt_str, data)
        return cls(outgauge_pack)

    def __init__(self, outgauge_list):
        self._set_vars = {}
        for f, op in zip(self.fields, outgauge_list):
            setattr(self, f, op)

    def to_struct(self):
        return struct.pack(self.fmt_str, *self.to_list())

    def to_list(self):
        return [self.__getattr__(f) for f in self.fields]

    def __getattr__(self, item):
        if item in self.fields:
            if item in self._set_vars:
                return self._set_vars[item]
            else:
                return 0
        else:
            super().__getattribute__(item)

    def __setattr__(self, key, value):
        if key in self.fields:
            self._set_vars[key] = value
        else:
            super().__setattr__(key, value)

    def __str__(self):
        return f"OutGaugePacket<{self.to_list()}>"

    def __repr__(self):
        return self.__str__()
