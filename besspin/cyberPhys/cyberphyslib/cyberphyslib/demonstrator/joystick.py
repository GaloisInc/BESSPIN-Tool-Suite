"""
Project: SSITH CyberPhysical Demonstrator
joystick.py
Author: Ethan Lew <elew@galois.com>
Date: 05/28/2021
Python 3.8.3
O/S: Windows 10

User Inputs Activity Monitoring Component
"""
import collections
import enum
import pygame
import abc
from collections import deque
import numpy as np
from .component import ComponentPoller, ComponentStatus
import cyberphyslib.demonstrator.component as ccomp
import cyberphyslib.demonstrator.config as cconf
from cyberphyslib.demonstrator.logger import jmonitor_logger
from cyberphyslib.demonstrator.simulator import BeamNgCommand
import cyberphyslib.canlib as ccan


class T150Axes(enum.IntEnum):
    """axis indicies for T150 Thrustmaster"""
    STEERING_WHEEL = 0
    BRAKE = 1
    THROTTLE = 2


def init_joystick(joy_name: str) -> pygame.joystick.Joystick:
    """get pygame joystick object from device name string"""
    pygame.init()

    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    tm_joy = []

    for joy in joysticks:
        joy.init()
        if joy.get_name() == joy_name:
            if not tm_joy:
                jmonitor_logger.warning(f"More than one racing wheel '{joy_name}' is connected!")
            tm_joy.append(joy)
    if not tm_joy:
        raise RuntimeError(f"No racing wheel '{joy_name}' is connected!")
    return tm_joy


class ActivityMonitor(abc.ABCMeta):
    """Monitor for User Activity Detection"""
    @property
    @abc.abstractmethod
    def is_active(self):
        return False

    @property
    def is_inactive(self):
        return not self.is_active


class WindowMonitor():
    """monitors a vector stream for activity (used inside of activity monitors)"""

    def __init__(self, window_length = 50, threshold = 1E-2):
        self.maxlen = window_length
        self.window = collections.deque([], maxlen=self.maxlen)
        self.threshold = threshold

    def update(self, val):
        self.window.append(val)

    @property
    def is_active(self):
        """evaluate activity condition"""
        if np.array(len(self.window) < self.maxlen).all():
            return True
        else:
            warr = np.array(self.window)
            rge = np.max(warr, axis=0) - np.min(warr, axis=0)
            if (rge > self.threshold).any():
                return True
            return False


class PedalMonitorComponent(ComponentPoller):
    def __init__(self, window_length = 50, threshold=1E-2):
        super().__init__("pmonitor", [cconf.BEAMNG_COMPONENT_SENSORS, (cconf.DIRECTOR_PORT, "pmonitor-commands")],
                         [(cconf.PMONITOR_PORT, "pmonitor-events"),
                          (cconf.PMONITOR_PORT, "pmonitor-beamng")],
                         sample_frequency=60.0)
        self._sensor_electrics = None
        self.window_length = window_length
        self.threshold = threshold
        self.window = None
        self.brake_value = None
        self.throttle_value = None
        self.gear_value = None

    def on_start(self):
        """start pollrt"""
        self.start_poller()
        self.window = WindowMonitor(window_length=self.window_length, threshold=self.threshold)

    def on_poll_poll(self, t):
        """fill up window of steering wheel observations"""
        edge = self.is_active
        if (self.brake_value is not None and self.throttle_value is not None and self.gear_value is not None):
            self.window.update([self.throttle_value, self.brake_value, self.gear_value])
        if edge is not self.is_active:
            if edge:
                jmonitor_logger.info("falling edge (transition inactive)")
                self.send_message(ccomp.Message(BeamNgCommand.TRANSITION_INACTIVE), "pmonitor-beamng")
            else:
                jmonitor_logger.info("rising edge (transition active)")
                self.send_message(ccomp.Message(BeamNgCommand.TRANSITION_ACTIVE), "pmonitor-beamng")

    @recv_topic("beamng-sensors")
    def _(self, msg, t):
        """subscribe to sim service sensor electrics"""
        self._sensor_electrics = msg.message

    @property
    def is_active(self):
        """evaluate activity condition
        TODO: make an abstract base class here?
        """
        return self.window.is_active if self.window else False

    @recv_can(ccan.CAN_ID_BRAKE_INPUT, ccan.CAN_FORMAT_BRAKE_INPUT)
    def _(self, data):
        self.brake_value = data[0]

    @recv_can(ccan.CAN_ID_THROTTLE_INPUT, ccan.CAN_FORMAT_THROTTLE_INPUT)
    def _(self, data):
        self.throttle_value = data[0]

    @recv_can(ccan.CAN_ID_GEAR, ccan.CAN_FORMAT_GEAR)
    def _(self, data):
        self.gear_value = data[0]


class JoystickMonitorComponent(ComponentPoller):
    """Activity Monitor for the Steering Wheel

    Sample at an update rate, filling up a window of n length. If range is less
    than a threshold, output an inactive status. Otherwise, output an active status.
    """
    update_rate = 2

    def __init__(self, joy_name: str, window_length = 50, threshold=1E-2):
        super().__init__("jmonitor", [(cconf.DIRECTOR_PORT, "jmonitor-commands")],
                                       [(cconf.JMONITOR_PORT, "jmonitor-events"),
                                        (cconf.JMONITOR_PORT, "jmonitor-beamng")],
                         sample_frequency= self.update_rate)
        # TODO: log joy info
        self._no_joystick = True
        self.joy_name = joy_name
        self.joystick = None
        self.window_length = window_length
        self.threshold = threshold
        self.window = None

    def on_start(self):
        """initialize pygame"""
        pygame.init()
        self.start_poller()
        try:
            self.joystick = init_joystick(self.joy_name)
            self._no_joystick = False
            self.window = [WindowMonitor(window_length=self.window_length, threshold=self.threshold) for _ in range(len(self.joystick))]
        except Exception as exc:
            self.joystick =  None
            self._no_joystick = True

    def wait_ready_command(self):
        import time
        while not self._start_finished:
            time.sleep(0.5)
        return ComponentStatus.READY if not self._no_joystick else ComponentStatus.ERROR

    def on_poll_poll(self, t):
        """fill up window of steering wheel observations"""
        edge = self.is_active
        if self.joystick:
            for idx, joy in enumerate(self.joystick):
                _ = pygame.event.get() # TODO: is this necessary?
                ret = [joy.get_axis(idx) for idx in range(joy.get_numaxes())]
                self.window[idx].update(ret)
        if edge is not self.is_active:
            if edge:
                jmonitor_logger.info("falling edge (transition inactive)")
                self.send_message(ccomp.Message(BeamNgCommand.TRANSITION_INACTIVE), "jmonitor-beamng")
            else:
                jmonitor_logger.info("rising edge (transition active)")
                self.send_message(ccomp.Message(BeamNgCommand.TRANSITION_ACTIVE), "jmonitor-beamng")

    @property
    def is_active(self):
        """evaluate activity condition"""
        return np.array([w.is_active for w in self.window]).any() if self.window else False
