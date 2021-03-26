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
import pathlib
from cyberphys import config, component, message, logger, canspecs

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


class BeamNgCommand(enum.Enum):
    """BeamNGComponent Commands"""
    RESTART = enum.auto()
    START = enum.auto()
    STOP = enum.auto()
    TOGGLE_PAUSE = enum.auto()
    REQUEST_STATE = enum.auto()


class BeamNgState(enum.Enum):
    """BeamNG Scenario State"""
    SCENARIO_RUNNING = enum.auto()
    SCENARIO_PAUSED = enum.auto()
    SCENARIO_STOPPED = enum.auto()


def requires_running_scenario(func):
    """guard Sim methods that requires a running scenario (e.g. poll sensors)"""
    @functools.wraps(func)
    def inner(self, *args, **kwargs):
        if self._beamng_session.skt is not None:
            return func(self, *args, **kwargs)
    return inner


class Sim(component.ComponentPoller):
    beamng_process_name = (pathlib.Path(config.BEAMNG_PATH) / "Bin64" / "BeamNG.research.x64.exe").resolve()
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
        self._beamng_session = None
        self._scenario = None
        self._vehicle = None
        self._location = None
        self._sensors = None
        self._scenario = None
        self.sensor_output = None
        self.color = [0.,]*3
        self.control = {}
        self.control_evt = True

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
                      "user": config.BEAMNG_USER_PATH }
        self._beamng_context = BeamNGpy('localhost', config.BEAMNG_PORT, **bng_args)


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
            assert not self.stopped
            self._beamng_session = self._beamng_context.open(launch=True)
            self._beamng_session.hide_hud()

            # Load and start the scenario
            assert not self.stopped
            self._beamng_session.load_scenario(self._scenario)
            self._beamng_session.set_relative_camera((-0.3, -.5, 0.95))
            self._beamng_session.start_scenario()

            assert not self.stopped
            self._beamng_session.resume()

            assert self._vehicle.skt
        except Exception as exc:
            logger.sim_logger.error(f"Failed to create BeamNG session and load scenario <{exc}>")

    def on_poll_poll(self, t):
        """simulator mainloop"""
        while not self.stopped:
            try:
                if (self._vehicle is not None) and (self._vehicle.skt):
                    if self.control_evt and self.control != {}:
                        self._vehicle.control(**self.control)
                        self.control_evt = False
                        self.control = {}
                self.sensor_output = self._beamng_session.poll_sensors(self._vehicle)
                self.send_message(message.Message(self.sensor_output["electrics"]),
                                "beamng-sensors")

                self._vehicle.update_vehicle()
                self._location = (tuple(self._vehicle.state["pos"]), tuple(self._vehicle.state["dir"]))
                self.send_message(message.Message(self._location),"beamng-vehicle")
            except ConnectionAbortedError:
                self.exit()
            except Exception as exc:
                pass

    def on_poll_exit(self) -> None:
        """beamNG exit method"""
        logger.sim_logger.info(f"{self.__class__.__name__} Exit Signal Received. This might take a while...")
        if self._beamng_session is not None:
            self._beamng_session.close()
        if self._beamng_context is not None:
            self._beamng_context.kill_beamng()
        #self.kill_beamng()
        #is_in_loop = True
        #while self._beamng_session is None and (self._beamng_context is not None or self._beamng_session is not None):
        #    if is_in_loop:
        #        logger.sim_logger.info(f"{self.__class__.__name__} Waiting for BeamNG context to terminate...")
        #        is_in_loop = False
        #    continue
        #self.stop_poller()

    ########## can receive ###########
    def control_process(self, name, data, bounds=(0.0, 1.0)):
        data = min(max(data[0], bounds[0]), bounds[1])
        self.control[name] = data
        self.control_evt = True

    @recv_can(canspecs.CAN_ID_STEERING_INPUT, "!b")
    def _(self, data):
        """steering -1.0, 1.0"""
        data = (float(data[0])/100.0,)
        return self.control_process("steering", data, bounds=(-1.0, 1.0))

    @recv_can(canspecs.CAN_ID_THROTTLE_INPUT, "!B")
    def _(self, data):
        """throttle [0..100] -> 0.0, 1.0"""
        data = (float(data[0])/100.0,)
        return self.control_process("throttle", data)

    @recv_can(canspecs.CAN_ID_BRAKE_INPUT, "!B")
    def _(self, data):
        """brake [0..100] -> 0.0, 1.0"""
        data = (float(data[0])/100.0,)
        return self.control_process("brake", data)

    @recv_can(canspecs.CAN_ID_GEAR, "!c")
    def _(self, data):
        """gear [P, R, N, D] -> -1, 5"""
        val, = data
        gear_map = {b'P': 1, b'R': -1, b'N': 0, b'D': 2}
        gear = gear_map.get(val, 0)
        return self.control_process("gear", (gear,), bounds=(-1, 5))

    ########## register topic receive methods ##########
    @recv_topic("beamng-commands")
    def _(self, msg, t):
        print(f"Received BeamNG Command {msg}")

    @recv_topic("beamng-commands", BeamNgCommand.RESTART)
    def _(self, t):
        self._beamng_session.restart_scenario()

    @recv_topic("beamng-commands", BeamNgCommand.STOP)
    def _(self, t):
        self._beamng_session.stop_scenario()

    @recv_topic("beamng-commands", BeamNgCommand.START)
    def _(self, t):
        self.start_session()

    @recv_topic("beamng-commands", BeamNgCommand.TOGGLE_PAUSE)
    def _(self, t):
        if self._is_paused:
            self._beamng_session.resume()
        else:
            self._beamng_session.pause()
        self._is_paused = not self._is_paused

    @recv_topic("beamng-commands", BeamNgCommand.REQUEST_STATE)
    def _(self, t):
        """state can be inferred from _beamng_session"""
        if self._beamng_session is not None and self._beamng_session.scenario is not None:
            if self._is_paused:
                state = BeamNgState.SCENARIO_PAUSED
            else:
                state = BeamNgState.SCENARIO_RUNNING
        else:
            state = BeamNgState.SCENARIO_STOPPED
        self.send_message(message.Message(state), 'beamng-state')
