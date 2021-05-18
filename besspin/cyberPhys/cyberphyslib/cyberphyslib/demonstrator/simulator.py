"""
Project: SSITH CyberPhysical Demonstrator
Name: simulator.py
Author: Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Date: 10/01/2020

Python 3.8.3
O/S: Windows 10

This routine creates a BeamNG simulator thread and makes vehicle speed,
throttle, brakes, and position available.
"""
import logging.config

import logging
import enum
import functools
import psutil
import time
import os
from cyberphyslib.demonstrator import config, component, message, logger
import cyberphyslib.canlib.canspecs as canspecs

from beamngpy import BeamNGpy, Scenario, Vehicle
from beamngpy.sensors import Electrics, GForces


class BeamNgStatus(enum.Enum):
    """BeamNgComponent Statuses"""
    EXIT_FINISHED = enum.auto()
    LAUNCH_FINISHED = enum.auto()
    READY = enum.auto()
    SENSOR_START = enum.auto()
    SENSOR_POLL = enum.auto()
    SENSOR_END = enum.auto()
    ERROR = enum.auto()
    OS_ERROR = enum.auto()
    RESTART_FINISHED = enum.auto()
    RESTART_FAILED = enum.auto()
    RESTART_INVALID = enum.auto()
    IS_AUTOPILOT = enum.auto()
    IS_MANUAL = enum.auto()


class BeamNgCommand(enum.Enum):
    """BeamNGComponent Commands"""
    RESTART = enum.auto()
    START = enum.auto()
    STOP = enum.auto()
    TOGGLE_PAUSE = enum.auto()
    REQUEST_STATE = enum.auto()
    WAIT_READY = enum.auto()
    ENABLE_AUTOPILOT = enum.auto()
    DISABLE_AUTOPILOT = enum.auto()
    UI_BUTTON_PRESSED = enum.auto()
    AUTOPILOT_STATUS = enum.auto()


def requires_running_scenario(func):
    """guard Sim methods that requires a running scenario (e.g. poll sensors)"""
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self._beamng_context.skt is not None:
            return func(self, *args, **kwargs)
    return inner


class Sim(component.ComponentPoller):
    beamng_process_name = "BeamNG.tech.x64.exe"
    @staticmethod
    def is_running_beamng():
        """returns whether BeamNG process is running"""
        try:
            return Sim.beamng_process_name in (p.name() for p in psutil.process_iter())
        except Exception:
            return False

    @staticmethod
    def kill_beamng(attempts=2):
        """kill BeamNG process if it's running"""
        if Sim.is_running_beamng():
            os.system(f"taskkill /im {Sim.beamng_process_name}")
            time.sleep(1)
            if Sim.is_running_beamng():
                if attempts > 0:
                    logging.warning(f"kill_beamng failed. Trying again...")
                    Sim.kill_beamng(attempts=attempts - 1)
                else:
                    # TODO: error handling system?
                    raise RuntimeError(f"task_kill_beamng failed")

    in_descr = config.BEAMNG_COMPONENT_INPUT
    out_descr = config.BEAMNG_COMPONENT_OUTPUT

    def __init__(self):
        self.port = config.BEAMNG_PORT
        self.path = config.BEAMNG_PATH

        # component network setup
        super().__init__("beamng", self.in_descr, self.out_descr, sample_frequency=120.0)

        self._beamng_context = None
        self._scenario = None
        self._vehicle = None
        self._location = None
        self._sensors = None
        self._scenario = None
        self.sensor_output = None
        self.color = [0.,]*3
        self.control = {}
        self.control_evt = True
        self._start_finished = False
        self._enable_autopilot = False
        self._disable_autopilot = False
        self._in_autopilot = False
        self._restart_scenario  = False
        self.beamng_start_finished = False

        # record whether sim is paused or not
        self._is_paused = False

    def on_start(self) -> None:
        if not self.stopped:
            self.start_poller()

    def on_poll_start(self) -> None:
        """beamNG session and scenario load

        NOTE: mainloop is included here due to thread access conflicts in on_poll
        """
        bng_args = { "home": config.BEAMNG_PATH,
                      "user": config.BEAMNG_USER_PATH}
        self._beamng_context = BeamNGpy('localhost', config.BEAMNG_PORT, **bng_args)
        self._beamng_context.open()

        self._scenario = Scenario('italy', 'SSITH',
                                  description='Drive protected.')
        self._vehicle = Vehicle('ego_vehicle', licence='SSITH', **config.BEAMNG_VEHICLE_CONFIG,
                                color='Red')

        gforces = GForces()
        electrics = Electrics()

        # Attach them
        self._vehicle.attach_sensor('gforces', gforces)
        self._vehicle.attach_sensor('electrics', electrics)

        self._scenario.add_vehicle(self._vehicle,
                                   **config.BEAMNG_ITALY_SPAWNPOINTS[config.BEAMNG_SCENARIO_SPAWNPOINT])

        # Compile the scenario and place it in BeamNG's map folder
        self._scenario.make(self._beamng_context)

        try:

            # Start BeamNG and enter the main loop
            assert not self.polling_thread.stopped
            self._beamng_context.hide_hud()

            # Load and start the scenario
            assert not self.polling_thread.stopped
            self._beamng_context.load_scenario(self._scenario)
            self._beamng_context.set_relative_camera((-0.3, -.5, 0.95))
            self._beamng_context.start_scenario()

            assert not self.polling_thread.stopped
            self._beamng_context.resume()

            assert self._vehicle.skt
            self._vehicle.connect(self._beamng_context)

            self.beamng_start_finished = True
            self.send_message(message.Message(BeamNgStatus.READY), 'beamng-events')
        except Exception as exc:
            logger.sim_logger.error(f"Failed to create BeamNG session and load scenario <{exc}>")
            self.send_message(message.Message(BeamNgStatus.OS_ERROR), 'beamng-events')
            self.kill_beamng()

    def on_poll_poll(self, t):
        """simulator mainloop"""
        while not self.polling_thread.stopped:
            try:
                # handle autopilot request
                # NOTE: restarts the scenario
                if self._enable_autopilot:
                    self._vehicle.ai_set_mode('span')
                    self._enable_autopilot = False
                    self._disable_autopilot = False
                    self._in_autopilot = True

                elif self._disable_autopilot:
                    self._vehicle.ai_set_mode('disabled')
                    self._disable_autopilot = False
                    self._enable_autopilot = False
                    self._in_autopilot = False

                if self._restart_scenario:
                    self._restart_scenario = False
                    self._beamng_context.restart_scenario()

                # handle vehicle control event
                if (self._vehicle is not None) and (self._vehicle.skt):
                    # do not control vehicle if in autopilot
                    if self.control_evt and self.control != {} and not self._in_autopilot:
                        self._vehicle.control(**self.control)
                        self.control_evt = False
                        self.control = {}

                self.sensor_output = self._beamng_context.poll_sensors(self._vehicle)
                self.send_message(message.Message(self.sensor_output["electrics"]),
                                "beamng-sensors")

                self._vehicle.update_vehicle()
                self._location = (tuple(self._vehicle.state["pos"]), tuple(self._vehicle.state["dir"]))
                self.send_message(message.Message(self._location), "beamng-vehicle")
            except ConnectionAbortedError:
                self.exit()
            except Exception as exc:
                pass

    def on_poll_exit(self) -> None:
        """beamNG exit method"""
        logger.sim_logger.info(f"{self.__class__.__name__} Exit Signal Received. This might take a while...")
        self.kill_beamng()
        if self._beamng_context is not None:
            self._beamng_context.close()

    def exit(self):
        super(Sim, self).exit()

    ########## can receive ###########
    def control_process(self, name, data, bounds=(0.0, 1.0)):
        data = min(max(data[0], bounds[0]), bounds[1])
        self.control[name] = data
        self.control_evt = True

    @recv_can(canspecs.CAN_ID_STEERING_INPUT, canspecs.CAN_FORMAT_STEERING_INPUT)
    def _(self, data):
        """steering -1.0, 1.0"""
        data = (float(data[0])/100.0,)
        return self.control_process("steering", data, bounds=(-1.0, 1.0))

    @recv_can(canspecs.CAN_ID_THROTTLE_INPUT, canspecs.CAN_FORMAT_THROTTLE_INPUT)
    def _(self, data):
        """throttle [0..100] -> 0.0, 1.0"""
        data = (float(data[0])/100.0,)
        return self.control_process("throttle", data)

    @recv_can(canspecs.CAN_ID_BRAKE_INPUT, canspecs.CAN_FORMAT_BRAKE_INPUT)
    def _(self, data):
        """brake [0..100] -> 0.0, 1.0"""
        data = (float(data[0])/100.0,)
        return self.control_process("brake", data)

    @recv_can(canspecs.CAN_ID_GEAR, canspecs.CAN_FORMAT_GEAR)
    def _(self, data):
        """gear [P, R, N, D] -> -1, 5"""
        val, = data
        gear_map = {b'P': 1, b'R': -1, b'N': 0, b'D': 2}
        gear = gear_map.get(val, 0)
        return self.control_process("gear", (gear,), bounds=(-1, 5))

    ########## register topic receive methods ##########
    def wait_ready_command(self):
        """wait until the service has finished booting"""
        import time
        while not self.beamng_start_finished:
            time.sleep(0.2)
        return component.ComponentStatus.READY

    def restart_command(self):
        try:
            if self._start_finished:
                self._restart_scenario = True
            else:
                return BeamNgStatus.RESTART_INVALID
        except Exception as exc:
            return BeamNgStatus.RESTART_FAILED
        return BeamNgStatus.RESTART_FINISHED

    def toggle_pause_command(self):
        """pause the simulator"""
        if self._start_finished:
            if self._is_paused:
                self._beamng_context.resume()
            else:
                self._beamng_context.pause()
            self._is_paused = not self._is_paused
            return BeamNgStatus.READY
        else:
            return BeamNgStatus.ERROR

    def enable_autopilot_command(self):
        if self._start_finished:
            self._enable_autopilot = True
        return BeamNgStatus.READY

    def disable_autopilot_command(self):
        """disable the autopilot"""
        if self._start_finished:
            self._disable_autopilot = True
        return BeamNgStatus.READY

    def autopilot_status_command(self):
        """disable the autopilot"""
        if self._in_autopilot:
            return message.Message(BeamNgStatus.IS_AUTOPILOT)
        return BeamNgStatus.IS_MANUAL

    def ui_button_pressed_command(self):
        if self._start_finished:
            if self._in_autopilot:
                self._disable_autopilot = True
                self._in_autopilot = None

    @recv_topic("beamng-commands", BeamNgCommand.RESTART)
    def _(self, t):
        """restart the scenario"""
        return message.Message(self.restart_command())

    @recv_topic("beamng-commands", BeamNgCommand.WAIT_READY)
    def _(self, t):
        """wait until the service has finished booting"""
        return message.Message(self.wait_ready_command())

    @recv_topic("beamng-commands", BeamNgCommand.TOGGLE_PAUSE)
    def _(self, t):
        """pause the simulator"""
        return message.Message(self.toggle_pause_command())

    @recv_topic("beamng-commands", BeamNgCommand.ENABLE_AUTOPILOT)
    def _(self, t):
        return message.Message(self.enable_autopilot_command())

    @recv_topic("beamng-commands", BeamNgCommand.DISABLE_AUTOPILOT)
    def _(self, t):
        """disable the autopilot"""
        return message.Message(self.disable_autopilot_command())

    @recv_topic("beamng-commands", BeamNgCommand.AUTOPILOT_STATUS)
    def _(self, t):
        """disable the autopilot"""
        return message.Message(self.autopilot_status_command())

    @recv_topic("infoui-beamng", BeamNgCommand.UI_BUTTON_PRESSED)
    def _(self, t):
        if self._start_finished:
            if self._in_autopilot:
                self._disable_autopilot = True
                self._in_autopilot = None
                self.restart_command()
