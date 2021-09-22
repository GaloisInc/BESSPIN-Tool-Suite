"""
Project: SSITH CyberPhysical Demonstrator
director.py
Author: Ethan Lew <elew@galois.com>
Date: 04/05/2021
Python 3.8.3
O/S: Windows 10

Interface to manage ignition components
"""

import time
import struct
import can as extcan

from enum import Enum, auto

import cyberphyslib.demonstrator.can as ccan
import cyberphyslib.demonstrator.simulator as simulator
import cyberphyslib.demonstrator.speedometer as speedo
import cyberphyslib.demonstrator.leds_manage as ledm
import cyberphyslib.demonstrator.infotainment as infotainment
import cyberphyslib.demonstrator.can_out as ccout
import cyberphyslib.demonstrator.component as ccomp
import cyberphyslib.demonstrator.config as cconf
import cyberphyslib.demonstrator.joystick as cjoy
import cyberphyslib.demonstrator.healthmonitor as cyhealth
import cyberphyslib.demonstrator.teensy as cteensy
import cyberphyslib.demonstrator.component as ccomp
import cyberphyslib.canlib as canlib

from cyberphyslib.demonstrator.handler import ComponentHandler
from cyberphyslib.demonstrator.logger import ignition_logger


class ComponentStatus(Enum):
    """
    HEALHY - the component is operating properly and errors should be cleared
    RESTARTING - the component is in the process of restarting
    UNHEALTHY - the component is unhealthy and an error should be reported
    UNKNOWN - we don't know the status of the component (uncommon)
    """
    HEALTHY = auto()
    RESTARTING = auto()
    UNHEALTHY = auto()
    UNKNWON = auto()

class ComponentHealthTracker():
    """
    name - component name as defined in Canlib
    can_id - as defined in Canlib
    status - status of the component
    time_of_reset - when was last reset requested
    max_wait_after_reset - how long can we wait after a reset
        until the component is considered unhealthy (to avoid false
        positives after a reset)
    """
    name = "componentName"
    cid = 0
    status = ComponentStatus.UNKNWON
    time_of_reset = None
    DEFAULT_WAIT_TIME = 10.0

    def __init__(self, cid, max_wait_after_reset=DEFAULT_WAIT_TIME, can_be_reset=True):
        self.name = canlib.CanlibComponentNames.get(cid,"UnknownComponent")
        self.cid = cid
        self.can_be_reset = can_be_reset
        self.max_wait_after_reset = max_wait_after_reset

    def __str__(self):
        end_color = '\033[0m'
        if self.status == ComponentStatus.HEALTHY:
            status = "HEALTHY"
            color = '\033[92m'
        elif self.status == ComponentStatus.RESTARTING:
            status = "RESTARTING"
            color = '\033[93m'
        elif self.status == ComponentStatus.UNHEALTHY:
            status = "UNHEALTHY"
            color = '\033[91m'
        elif self.status == ComponentStatus.UNKNWON:
            status = "UNKNWON"
            color = '\033[94m'
        else:
            status = "UNDEFINED"
            color = '\033[95m'
        return f"{self.name} : {color} {status} {end_color}"

class IgnitionDirector():
    """
    Ignition program that implements the desired execution flow.
    The simplified state machine is now implemented without the `transitions` module
    """
    hacks2patterns = {
        canlib.HACK_NONE: ledm.LedPatterns.NOMINAL,
        #canlib.HACK_OTA: ledm.LedPatterns.NOMINAL, # TODO: add pattern for OTA hack?
        canlib.HACK_BRAKE: ledm.LedPatterns.BRAKE_HACK,
        canlib.HACK_THROTTLE: ledm.LedPatterns.THROTTLE_HACK,
        canlib.HACK_TRANSMISSION: ledm.LedPatterns.TRANSMISSION_HACK,
        canlib.HACK_LKAS: ledm.LedPatterns.STEERING_HACK,
        #canlib.HACK_INFOTAINMENT_1: ledm.LedPatterns.ALL_ON,# TODO: add pattern for infotainment hack
        #canlib.HACK_INFOTAINMENT_2: ledm.LedPatterns.ALL_ON,# TODO add pattern for infotainment hack
    }

    HEALTH_MONITOR_FREQUENCY = 0.1 # Every 10s
    HEART_RATE_FREQUENCY = 1.0 # Every 1s

    minimal_functionality_systems = {
        canlib.CAN_DISPLAY_FRONTEND: ComponentHealthTracker(cid=canlib.CAN_DISPLAY_FRONTEND,can_be_reset=False),
        canlib.CAN_DISPLAY_BACKEND: ComponentHealthTracker(cid=canlib.CAN_DISPLAY_BACKEND,can_be_reset=False),
        canlib.HACKER_KIOSK_FRONTEND: ComponentHealthTracker(cid=canlib.HACKER_KIOSK_FRONTEND,can_be_reset=False),
        canlib.HACKER_KIOSK_BACKEND: ComponentHealthTracker(cid=canlib.HACKER_KIOSK_BACKEND,can_be_reset=False),
        canlib.TEENSY: ComponentHealthTracker(cid=canlib.TEENSY)
    }

    medium_functionality_systems = {
        canlib.BESSPIN_TOOL_FREERTOS: ComponentHealthTracker(cid=canlib.BESSPIN_TOOL_FREERTOS,can_be_reset=False),
        canlib.FREERTOS_1: ComponentHealthTracker(cid=canlib.FREERTOS_1, max_wait_after_reset=60),
        canlib.FREERTOS_2_CHERI: ComponentHealthTracker(cid=canlib.FREERTOS_2_CHERI, max_wait_after_reset=60),
        canlib.FREERTOS_3: ComponentHealthTracker(cid=canlib.FREERTOS_3, max_wait_after_reset=60),
    }

    full_functionality_systems = {
        canlib.DEBIAN_1: ComponentHealthTracker(cid=canlib.DEBIAN_1,can_be_reset=False),
        canlib.DEBIAN_2_LMCO: ComponentHealthTracker(cid=canlib.DEBIAN_2_LMCO,can_be_reset=False),
        canlib.DEBIAN_3: ComponentHealthTracker(cid=canlib.DEBIAN_3,can_be_reset=False),
        canlib.BESSPIN_TOOL_DEBIAN: ComponentHealthTracker(cid=canlib.BESSPIN_TOOL_DEBIAN,can_be_reset=False),
        canlib.INFOTAINMENT_THIN_CLIENT: ComponentHealthTracker(cid=canlib.INFOTAINMENT_THIN_CLIENT,can_be_reset=False),
        canlib.INFOTAINMENT_SERVER_1: ComponentHealthTracker(cid=canlib.INFOTAINMENT_SERVER_1, max_wait_after_reset=30),
        canlib.INFOTAINMENT_SERVER_2: ComponentHealthTracker(cid=canlib.INFOTAINMENT_SERVER_2, max_wait_after_reset=30),
        canlib.INFOTAINMENT_SERVER_3: ComponentHealthTracker(cid=canlib.INFOTAINMENT_SERVER_3, max_wait_after_reset=30),
        canlib.OTA_UPDATE_SERVER_1: ComponentHealthTracker(cid=canlib.OTA_UPDATE_SERVER_1, max_wait_after_reset=30),
        canlib.OTA_UPDATE_SERVER_2: ComponentHealthTracker(cid=canlib.OTA_UPDATE_SERVER_2, max_wait_after_reset=30),
        canlib.OTA_UPDATE_SERVER_3: ComponentHealthTracker(cid=canlib.OTA_UPDATE_SERVER_3, max_wait_after_reset=30),
        canlib.INFOTAINMENT_BACKEND: ComponentHealthTracker(cid=canlib.INFOTAINMENT_BACKEND,can_be_reset=False)
    }

    # Easter egg^_^
    race_car = False

    def set_race_car(self, race_car):
        self.race_car = race_car    

    @classmethod
    def from_network_config(cls, net_conf: cconf.DemonstratorNetworkConfig):
        """produce director from the Besspin environment setup file"""
        cmd_host, cmd_subscribers = net_conf.getCmdNetworkNodes("SimPc")
        ip_sim = net_conf.ip_SimPc
        can_port = net_conf.port_network_canbusPort
        info_port = net_conf.port_network_infotainmentUiPort
        return cls(cmd_host, cmd_subscribers, ip_sim, can_port, info_port,
                   ssith_info_whitelist=net_conf.wl_SSITH_INFO_WHITELIST + [net_conf.ip_InfotainmentThinClient],
                   ssith_ecu_whitelist=net_conf.wl_SSITH_ECU_WHITELIST + [net_conf.ip_InfotainmentThinClient],
                   base_whitelist=net_conf.wl_BASELINE + [net_conf.ip_InfotainmentThinClient],
                   apply_lists=cconf.APPLY_LISTS)

    @property
    def self_drive_mode(self):
        """self drive state exists in the sim service -- don't duplicate or invalidate this"""
        return self._handler["beamng"]._in_autopilot

    def __init__(self,
                 cmd_host,
                 cmd_nodes,
                 sim_ip,
                 can_port,
                 info_port,
                 ssith_info_whitelist=False,
                 ssith_ecu_whitelist=False,
                 base_whitelist=False,
                 ssith_info_blacklist=False,
                 ssith_ecu_blacklist=False,
                 base_blacklist=False,
                 apply_lists = True
                 ):

        self.can_multiverse = None
        self.info_net = None
        self.proxy = None
        self.can_port = can_port
        self.info_port = info_port

        # NOTE: there are inconsistencies between TcpBus and UdpBus arguments
        self.scenario_timeout = cconf.SCENARIO_TIMEOUT
        self.cc_timeout = cconf.CC_TIMEOUT

        # Need to know what is the active scenario
        # TODO: is there a better solution?
        self.active_scenario = canlib.SCENARIO_BASELINE
        self.self_drive_scenario_start = None
        self.system_functionality_level = canlib.FUNCTIONALITY_FULL

        self.joystick_name = cconf.JOYSTICK_NAME

        self._handler = ComponentHandler()

        sip = sim_ip
        can_ssith_info = ccan.CanUdpNetwork("secure_infotainment", can_port, sip)
        can_ssith_ecu = ccan.CanUdpNetwork("secure_ecu", can_port, sip)
        can_base = ccan.CanUdpNetwork("base", can_port, sip)
        networks = [can_base, can_ssith_ecu, can_ssith_info]

        if apply_lists:
            can_ssith_info.whitelist = ssith_info_whitelist
            can_ssith_ecu.whitelist = ssith_ecu_whitelist
            can_base.whitelist = base_whitelist
            can_ssith_info.blacklist = ssith_info_blacklist
            can_ssith_ecu.blacklist = ssith_ecu_blacklist
            can_base.blacklist = base_blacklist

        # start the can networks
        self.can_multiverse = ccan.CanMultiverse("multiverse", networks, default_network="base")
        self.info_net = ccan.CanUdpNetwork("info-net", self.info_port, sip, blacklist=[sim_ip])
        self.cmd_net = ccan.CanTcpNetwork("cc-net", cmd_host, cmd_nodes)

        self.is_finished = False
        self._noncrit = False

        # Frequency divider
        self.check_health_time = 0.0

        self.teensy = cteensy.TeensyMonitor()
        self.hm = cyhealth.HeartbeatMonitor()

    def start(self):
        """
        Start function
        - Initialize components
        - Start the periodic poller
        """
        if self.startup():
            ignition_logger.info("Startup successful: starting polling")
            # Clean the errors
            self.component_error_send(canlib.IGNITION, canlib.ERROR_NONE)
            self.main_loop()
        else:
            ignition_logger.error("A critical component failed. Terminating....")
            self.terminate()

    def main_loop(self):
        """main loop"""
        self.check_health_time = time.time()
        self.check_heartbeat_time = time.time()
        cnt = 0
        while (True):
            cnt += 1
            t = time.time()
            delta_t = t - self.check_health_time
            hr_delta_t = t - self.check_heartbeat_time

            # Process CMD messages
            self.process_cmd_message()

            # Process UDP CAN is done asynchronously in different components

            # Check driver activity
            self.check_driver_activity()

            if self.system_functionality_level < canlib.FUNCTIONALITY_MEDIUM:
                # If in minimal mode, read teensy data here
                sim: simulator.Sim = self._handler["beamng"]
                # NOTE: ugly!
                self.control['gear'] = self.teensy.gear
                self.control['throttle'] = self.teensy.throttle
                self.control['brake'] = self.teensy.brake
                self.control_evt = True

            # Heartbeat
            if hr_delta_t > (1/IgnitionDirector.HEART_RATE_FREQUENCY):
                self.check_heartbeat_time = t
                hr_msg = self.hm.component_monitor.get_req_msg()
                self.cmd_net.send_msg(hr_msg)
                self.can_multiverse.send_msg(hr_msg)

            # System health check
            if delta_t > (1/IgnitionDirector.HEALTH_MONITOR_FREQUENCY):
                self.system_health_check()
                self.check_health_time = t
                print(f"Main loop freq: {cnt/delta_t}[Hz]")
                cnt = 0

            # Approximately sleep
            time.sleep(0.04)


    def component_ready_send(self, component_id):
        """
        Send CAN_ID_CMD_COMPONENT_READY message
        """
        msg = extcan.Message(arbitration_id=canlib.CAN_ID_CMD_COMPONENT_READY,
                             dlc=canlib.CAN_DLC_CMD_COMPONENT_READY,
                             data=struct.pack(canlib.CAN_FORMAT_CMD_COMPONENT_READY,
                                              component_id))
        self.cmd_net.send_msg(msg)

    def component_restart_send(self, component_id):
        """
        Send CAN_ID_CMD_RESTART message
        """
        msg = extcan.Message(arbitration_id=canlib.CAN_ID_CMD_RESTART,
                             dlc=canlib.CAN_DLC_CMD_RESTART,
                             data=struct.pack(canlib.CAN_FORMAT_CMD_RESTART,
                                              component_id))
        self.cmd_net.send_msg(msg)

    def component_error_send(self, component_id, error_id):
        """
        Send CAN_ID_CMD_COMPONENT_ERROR message
        """
        msg = extcan.Message(arbitration_id=canlib.CAN_ID_CMD_COMPONENT_ERROR,
                             dlc=canlib.CAN_DLC_CMD_COMPONENT_ERROR,
                             data=struct.pack(canlib.CAN_FORMAT_CMD_COMPONENT_ERROR,
                                              component_id, error_id))
        self.cmd_net.send_msg(msg)

    def process_cmd_message(self):
        """process CMD message and:
        1) restart BeamNG
        2) update LED pattern
        3) switch active CAN network
        4) handle external component resets
        """
        recv = self.cmd_net.recv(timeout=self.cc_timeout)
        if recv:
            cid, msg = recv
            try:
                if cid == canlib.CAN_ID_CMD_RESTART:
                    ignition_logger.info(f"process cc: restart")
                    dev_id = struct.unpack(canlib.CAN_FORMAT_CMD_RESTART, msg.data)[0]
                    if dev_id == canlib.IGNITION:
                        ignition_logger.info("Director: restarting ignition from CMD_RESTART")
                        self.restart_simulator()
                    else:
                        if dev_id in self.minimal_functionality_systems:
                            self.minimal_functionality_systems[dev_id].status = ComponentStatus.RESTARTING
                            self.minimal_functionality_systems[dev_id].time_of_reset = time.time()
                        elif dev_id in self.medium_functionality_systems:
                            self.medium_functionality_systems[dev_id].status = ComponentStatus.RESTARTING
                            self.medium_functionality_systems[dev_id].time_of_reset = time.time()
                        elif dev_id in self.full_functionality_systems:
                            self.full_functionality_systems[dev_id].status = ComponentStatus.RESTARTING
                            self.full_functionality_systems[dev_id].time_of_reset = time.time()
                        else:
                            pass

                elif cid == canlib.CAN_ID_CMD_HACK_ACTIVE:
                    hack_idx = struct.unpack(canlib.CAN_FORMAT_CMD_HACK_ACTIVE, msg.data)[0]
                    ignition_logger.info(f"process cc: set hack active {hack_idx}")
                    # Process HACK_ACTIVE messages only in baseline scenario
                    if self.active_scenario == canlib.SCENARIO_BASELINE:
                        # NOTE:  treat Led manager as a critical component
                        lm: ledm.LedManagerComponent = self._handler["ledm"]
                        lm.update_pattern(ledm.LedPatterns(IgnitionDirector.hacks2patterns[hack_idx]))

                elif cid == canlib.CAN_ID_CMD_ACTIVE_SCENARIO:
                    nmap = {
                        canlib.SCENARIO_BASELINE: "base",
                        canlib.SCENARIO_SECURE_ECU: "secure_ecu",
                        canlib.SCENARIO_SECURE_INFOTAINMENT: "secure_infotainment"}
                    scen_idx = struct.unpack(canlib.CAN_FORMAT_CMD_ACTIVE_SCENARIO, msg.data)[0]
                    ignition_logger.info(f"process cc: active scenario {scen_idx}")
                    self.active_scenario = scen_idx
                    cm: ccan.CanMultiverseComponent = self._handler["canm"]
                    cm.select_network(nmap[scen_idx])
                    # Update LED patterns
                    lm: ledm.LedManagerComponent = self._handler["ledm"]
                    if scen_idx == canlib.SCENARIO_BASELINE:
                        pattern = ledm.LedPatterns.NOMINAL
                    else:
                        pattern = ledm.LedPatterns.SSITH
                    lm.update_pattern(ledm.LedPatterns(pattern))
                elif cid == canlib.CAN_ID_HEARTBEAT_ACK:
                    # Update response
                    client_id, req_num = struct.unpack(canlib.CAN_FORMAT_HEARTBEAT_ACK, msg.data)
                    self.hm.component_monitor.submit_response(client_id, (client_id, req_num))
                else:
                    pass
            except Exception as exc:
                ignition_logger.error(f"process cc: error with message {msg}: {exc}")

    def check_driver_activity(self):
        """
        If inactive, switch to self-drive
        If active, switch to manual drive
        If in self-drive, restart upon scenario timeout
        """
        # NOTE: if jmonitor has failed assume user input is present
        # TODO: will this work if the monitor doesn't initialize?
        activity = self._handler['jmonitor'].is_active or self._handler['pmonitor'].is_active

        # if in self drive mode and activity has occurred, get out
        if activity and self.self_drive_mode:
            ignition_logger.info("Director: activity detected, switching to manual")
            self.disable_autopilot()
        elif self.self_drive_mode:
            # Monitor for a scenario timeout
            if self.self_drive_scenario_start:
                if (time.time() - self.self_drive_scenario_start) > self.scenario_timeout:
                    ignition_logger.info("Director: Scenario timeout, restarting")
                    # Restart the car if self-driving for too long
                    self.restart_simulator()
                    self.self_drive_scenario_start = time.time()
        elif activity: # do nothing if user actvity is present
            pass
        else:
            ignition_logger.info("Director: no activity detected, switching to self-drive")
            self.enable_autopilot()

    def component_health_check(self, component_dictionary: dict, health_report: dict):
        """
        Iterate over components in the dictionry and perform checks
        """
        for cid in component_dictionary:
            component: ComponentHealthTracker = component_dictionary[cid]
            if cid in health_report:
                is_healthy: bool = health_report[cid]
                old_status = component.status
                if is_healthy:
                    # New report says component is healthy
                    if old_status == ComponentStatus.HEALTHY:
                        # no change here
                        pass
                    elif old_status == ComponentStatus.RESTARTING:
                        # restart was successfull!
                        self.component_error_send(cid, canlib.ERROR_NONE)
                        component.status = ComponentStatus.HEALTHY
                    elif old_status == ComponentStatus.UNHEALTHY:
                        # it is healthy now
                        self.component_error_send(cid, canlib.ERROR_NONE)
                        component.status = ComponentStatus.HEALTHY
                    elif old_status == ComponentStatus.UNKNWON:
                        component.status = ComponentStatus.HEALTHY
                else:
                    # New report says component is not healthy
                    if old_status == ComponentStatus.HEALTHY:
                        # Possibly request a reset here
                        # self.component_restart_send(cid)
                        self.component_error_send(cid, canlib.ERROR_UNSPECIFIED)
                        component.status = ComponentStatus.UNHEALTHY
                    elif old_status == ComponentStatus.RESTARTING:
                        # see how long ago was the reset
                        delta_t = time.time() - component.time_of_reset
                        if delta_t > component.max_wait_after_reset:
                            # too much time passed, mark as unhealthy
                            self.component_error_send(cid, canlib.ERROR_UNSPECIFIED)
                            component.status = ComponentStatus.UNHEALTHY
                    elif old_status == ComponentStatus.UNHEALTHY:
                        # no change here
                        pass
                    elif old_status == ComponentStatus.UNKNWON:
                        # notify
                        self.component_error_send(cid, canlib.ERROR_UNSPECIFIED)
                        component.status = ComponentStatus.UNHEALTHY
            else:
                component.status = ComponentStatus.UNKNWON
            ignition_logger.warn(component)

    def system_health_check(self):
        """
        Query system health, update functionality level if necessary
        """
        # # NOTE: this a patch to reset teensy when it gets stuck
        # if not self.teensy.is_healthy:
        #     ignition_logger.warning(f"Teensy is not healthy, restarting.")
        #     self.component_restart_send(canlib.TEENSY)
        #     self.component_error_send(canlib.TEENSY, canlib.ERROR_UNSPECIFIED)
        # else:
        #     self.component_error_send(canlib.TEENSY, canlib.ERROR_NONE)

        hr: dict  = self.hm.health_report
        # Get teensy information
        hr[canlib.TEENSY] = self.teensy.is_healthy

        self.component_health_check(self.minimal_functionality_systems, hr)
        self.component_health_check(self.medium_functionality_systems, hr)
        self.component_health_check(self.full_functionality_systems, hr)
        
        # Here we need to set the functionality level
        # iterate over components, if at least one UNHEALHY in each set, mark the level?

        # for cid, is_healthy in hr.items():
        #     if not is_healthy:
        #         # restart cid
        #         ignition_logger.warn(f"Need to send restart request to component {canlib.CanlibComponentNames[cid]}")

        # func_set = {k for k, v in hr.items() if v}
        # if (full_functionality_systems | medium_functionality_systems | minimal_functionality_systems).issubset(func_set):
        #     # we are fully functional
        #     ignition_logger.info("Ignition is at full functionality level")
        # elif (medium_functionality_systems | minimal_functionality_systems).issubset(func_set):
        #     # medium functionality
        #     ignition_logger.warn("Ignition is at medium functionality level")
        # elif (minimal_functionality_systems).issubset(func_set):
        #     # minimal functionality
        #     ignition_logger.warn("Ignition is at minimal functionality level")
        # else:
        #     ignition_logger.warn("Ignition is a null functionality level")

    def update_functionality_level(self, new_func_level):
        """
        Update system functionality level if Ignition component and its subcomponents
        """
        if new_func_level != self.system_functionality_level:
            levels = [canlib.FUNCTIONALITY_FULL,
                      canlib.FUNCTIONALITY_MEDIUM,
                      canlib.FUNCTIONALITY_MINIMAL,
                      canlib.FUNCTIONALITY_NONE
                      ]
            if new_func_level in levels:
                ignition_logger.info(f"Switching to {new_func_level}")
                sim: simulator.Sim = self._handler["beamng"]
                player: infotainment.InfotainmentPlayer = self._handler["infoplay"]
                player.update_functionality_level(new_func_level)
                sim.update_functionality_level(new_func_level)
                self.system_functionality_level = new_func_level
            else:
                ignition_logger.info(f"Unknown functionality level {new_func_level}, ignoring.")
                return

    def restart_simulator(self):
        """
        Restart BeamNG simulator (car back to the beginning)
        """
        ignition_logger.info("Restart simulator")
        sim: simulator.Sim = self._handler["beamng"]
        sim.restart_command()

    def enable_autopilot(self):
        """
        Enable autopilot
        """
        ignition_logger.info("Enable autopilot, disable sound")
        sim: simulator.Sim = self._handler["beamng"]
        sim.enable_autopilot_command()
        sim.restart_command()
        player: infotainment.InfotainmentPlayer = self._handler["infoplay"]
        player.enable_sound(False)
        self.self_drive_scenario_start = time.time()

    def disable_autopilot(self):
        """
        Disable autopilot
        """
        ignition_logger.info("Disable autopilot, enable sound")
        sim: simulator.Sim = self._handler["beamng"]
        sim.disable_autopilot_command()
        sim.restart_command()
        player: infotainment.InfotainmentPlayer = self._handler["infoplay"]
        player.enable_sound(True)
        self.self_drive_scenario_start = None

    def terminate(self):
        """
        Terminating ignition
        """
        self.component_error_send(canlib.IGNITION, canlib.ERROR_UNSPECIFIED)
        ignition_logger.info("Termination State: Enter")
        self.is_finished = True
        self._handler.exit()
        self.info_net.exit()

    def startup(self) -> bool:
        """
        Startup and initialize ignition
        """
        def register_components():
            # register call of the components to the CAN multiverse network
            for c in self._handler.components:
                if c.name != "canm":
                    self.can_multiverse.register(c)

        def start_component(comp):
            msg = self._handler.start_component(comp)
            if msg != ccomp.ComponentStatus.READY:
                ignition_logger.info(f"{comp.name} service failed to start ({msg})")
                self.input_noncrit_fail = False
                self.input_component_fail = True
                return False
            return True

        def start_noncrit_component(comp):
            if not start_component(comp):
                ignition_logger.info(f"{comp.name} Noncritical service failed to start")
                self.input_noncrit_fail = True
                self.input_component_fail = False
                if comp.name == 'jmonitor':
                    self.component_error_send(canlib.JOYSTICK_MONITOR,canlib.ERROR_UNSPECIFIED)
                elif comp.name == 'pmonitor':
                    self.component_error_send(canlib.PEDAL_MONITOR,canlib.ERROR_UNSPECIFIED)
                elif comp.name == 'speedo':
                    self.component_error_send(canlib.INSTRUMENT_CLUSTER,canlib.ERROR_UNSPECIFIED)
                else:
                    ignition_logger.info(f"Unexpected component name: {comp.name}")
                return False
            self.can_multiverse.register(comp)
            return True

        simulator.Sim.kill_beamng(1)

        # startup beamng
        if not start_component(simulator.Sim(self.race_car)): return False

        # startup the multiverse
        if not start_component(ccan.CanMultiverseComponent(self.can_multiverse)): return False

        # startup the can location poller
        if not start_component(ccout.CanOutPoller(self.can_multiverse)): return False

        # startup led manager
        if not start_component(ledm.LedManagerComponent.for_ignition()): return False

        # startup the heartbeat monitor
        self.hm.start()

        # startup infotainment proxy
        ui = infotainment.InfotainmentUi(self.can_multiverse)
        player = infotainment.InfotainmentPlayer(self.info_net)
        if not start_component(ui): return False
        if not start_component(player): return False

        # Teensy serial reader
        self.teensy.start()

        # add everything to the can multiverse network
        register_components()

        self.info_net.start()

        # startup the speedometer
        start_noncrit_component(speedo.Speedo())

        # startup the pedal monitor
        start_noncrit_component(cjoy.PedalMonitorComponent(window_length=1000))

        # startup the joystick monitor
        start_noncrit_component(cjoy.JoystickMonitorComponent(self.joystick_name))

        return True
