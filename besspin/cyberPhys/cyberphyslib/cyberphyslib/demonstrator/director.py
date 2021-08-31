"""
Project: SSITH CyberPhysical Demonstrator
director.py
Author: Ethan Lew <elew@galois.com>
Date: 04/05/2021
Python 3.8.3
O/S: Windows 10

Interface to manage ignition components
"""
import cyberphyslib.demonstrator.can as ccan
import cyberphyslib.demonstrator.simulator as simulator
import cyberphyslib.demonstrator.speedometer as speedo
import cyberphyslib.demonstrator.leds_manage as ledm
import cyberphyslib.demonstrator.infotainment as infotainment
import cyberphyslib.demonstrator.can_out as ccout
import cyberphyslib.demonstrator.component as ccomp
import cyberphyslib.demonstrator.config as cconf
import cyberphyslib.demonstrator.joystick as cjoy
import cyberphyslib.demonstrator.health as cyhealth
import cyberphyslib.canlib as canlib
import can as extcan

from cyberphyslib.demonstrator.handler import ComponentHandler
from cyberphyslib.demonstrator.logger import ignition_logger

#import transitions
from transitions.extensions import GraphMachine as Machine
from transitions import State

import time
import struct

class IgnitionDirector:
    """
    Ignition program that implements the desired execution flow

    IgnitionDirector is a Moore FSM with 9 states and 6 inputs, namely

        input = {component_fail, fadecandy_fail, scenario_timeout, cc_msg, can_msg, self_drive}
        state = {startup, noncrit_failure, ready, terminate, self_drive, restart, timeout, cc_msg, can}

    Two states whose transitions depend on input are startup and the ready state. Callbacks associated with this state
    machine are responsible for identifying the appropriate inputs based on the component behavior.
    """
    # FSM description
    states=[
        State(name='startup', on_enter='startup_enter'),
        State(name='ready', on_enter='ready_enter'),
        State(name='terminate', on_enter='terminate_enter'),
    ]

    transitions = [
        # startup logic
        { 'trigger': 'next_state', 'source': 'startup', 'dest': 'terminate',
          'conditions': 'input_component_fail' },
        { 'trigger': 'next_state', 'source': 'startup', 'dest': 'ready',
          'unless': ['input_component_fail', 'input_noncrit_fail'] },

        # ready logic
        {'trigger': 'next_state', 'source': 'ready', 'dest': 'ready',
         'unless': ['input_component_fail', 'input_noncrit_fail']},
    ]

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

    @classmethod
    def draw_graph(cls, fname: str):
        """draw a fsm graphviz graph (for documentation, troubleshooting)

        NOTE: you will need to install graphviz (with dot)
        """
        class TmpObj(object):
            pass
        machine = Machine(TmpObj(), states=cls.states,
                          transitions=cls.transitions, initial='startup', show_conditions=True)
        machine.get_graph().draw(fname, prog='dot')

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
        # TODO: FIXME: ugly access
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
        """ignition state machine"""
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
        self.system_functionality_level = canlib.FUNCTIONALITY_NONE

        self.joystick_name = cconf.JOYSTICK_NAME

        self._handler = ComponentHandler()
        self.machine = Machine(self, states=self.states, transitions=self.transitions, initial='startup', show_conditions=True)

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

        # input space as class members
        self.input_noncrit_fail = False
        self.input_component_fail = False

        self.is_finished = False
        self._noncrit = False

    def run(self):
        """start the state machine, and keep it transitioning until termination"""
        try:
            self.startup_enter()
            while not self.is_finished:
                # advance the state machine
                self.next_state()
        except KeyboardInterrupt:
            ignition_logger.info("Received keyboard interrupt. Terminating....")
            self.terminate_enter()

    def default_input(self):
        """input initialization"""
        self.input_noncrit_fail = False
        self.input_component_fail = False

    def draw_graph(self, fname: str):
        """draw a fsm graphviz graph (for documentation, troubleshooting)

        NOTE: you will need to install graphviz (with dot)
        """
        self.machine.get_graph().draw(fname, prog='dot')

    def component_ready_send(self, component_id):
        msg = extcan.Message(arbitration_id=canlib.CAN_ID_CMD_COMPONENT_READY,
                             dlc=canlib.CAN_DLC_CMD_COMPONENT_READY,
                             data=struct.pack(canlib.CAN_FORMAT_CMD_COMPONENT_READY,
                                              component_id))
        self.cmd_net.send_msg(msg)

    def component_error_send(self, component_id, error_id):
        msg = extcan.Message(arbitration_id=canlib.CAN_ID_CMD_COMPONENT_ERROR,
                             dlc=canlib.CAN_DLC_CMD_COMPONENT_ERROR,
                             data=struct.pack(canlib.CAN_FORMAT_CMD_COMPONENT_ERROR,
                                              component_id, error_id))
        self.cmd_net.send_msg(msg)

    def status_send(self, canid, argument):
        msg = extcan.Message(arbitration_id=canid, dlc=1, data=struct.pack("!B", argument))
        self.cmd_net.send_msg(msg)

    def process_cmd_message(self):
        """process CMD message and:
        1) restart BeamNG
        2) update LED pattern
        3) switch active CAN network
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

                elif cid == canlib.CAN_ID_CMD_HACK_ACTIVE:
                    hack_idx = struct.unpack(canlib.CAN_FORMAT_CMD_HACK_ACTIVE, msg.data)[0]
                    ignition_logger.info(f"process cc: set hack active {hack_idx}")
                    # Process HACK_ACTIVE messages only in baseline scenario
                    if self.active_scenario == canlib.SCENARIO_BASELINE:
                        # NOTE:  tread Led manager as a critical component
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

    def system_health_check(self):
        """
        Query system health, update functionality level if necessary
        """
        # TODO
        # self.update_functionality_level(new_level)
        # components = some_healthchec-query
        #
        minimal_functionality_systems = [
            canlib.CAN_DISPLAY_FRONTEND,
            canlib.CAN_DISPLAY_BACKEND,
            canlib.HACKER_KIOSK_FRONTEND,
            canlib.HACKER_KIOSK_BACKEND,
            # Teensy?
        ]
        medium_functionality_systems = [
            canlib.BESSPIN_TOOL_FREERTOS,
            canlib.FREERTOS_1,
            canlib.FREERTOS_2_CHERI,
            canlib.FREERTOS_3,
        ]
        full_functionality_systems = [
            canlib.DEBIAN_1,
            canlib.DEBIAN_2_LMCO,
            canlib.DEBIAN_3,
            canlib.BESSPIN_TOOL_DEBIAN,
            canlib.INFOTAINMENT_THIN_CLIENT,
            canlib.INFOTAINMENT_SERVER_1,
            canlib.INFOTAINMENT_SERVER_2,
            canlib.INFOTAINMENT_SERVER_3,
            canlib.OTA_UPDATE_SERVER_1,
            canlib.OTA_UPDATE_SERVER_2,
            canlib.OTA_UPDATE_SERVER_3,
            canlib.INFOTAINMENT_BACKEND
        ]
        # for component in base_systems:
        #     if component is not healthy:
        #         restart component

    def update_functionality_level(self, new_func_level):
        """
        Update system functionality level
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

### STATE ENTRY CALLBACKS
    def terminate_enter(self):
        self.component_error_send(canlib.IGNITION, canlib.ERROR_UNSPECIFIED)
        ignition_logger.info("Termination State: Enter")
        self.is_finished = True
        self._handler.exit()
        self.info_net.exit()

    def startup_enter(self):
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

        ignition_logger.info("Startup State: Enter")
        simulator.Sim.kill_beamng(1)

        # startup beamng
        if not start_component(simulator.Sim()): return

        # startup the multiverse
        if not start_component(ccan.CanMultiverseComponent(self.can_multiverse)): return

        # startup the can location poller
        if not start_component(ccout.CanOutPoller(self.can_multiverse)): return

        # startup led manager
        if not start_component(ledm.LedManagerComponent.for_ignition()): return

        # startup the heartbeat monitor
        if not start_component(cyhealth.HeartbeatMonitor(self.can_multiverse, self.cmd_net)): return

        # startup infotainment proxy
        ui = infotainment.InfotainmentUi(self.can_multiverse)
        player = infotainment.InfotainmentPlayer(self.info_net)
        if not start_component(ui): return
        if not start_component(player): return

        # add everything to the can multiverse network
        register_components()

        self.info_net.start()

        # startup the speedometer
        start_noncrit_component(speedo.Speedo())

        # startup the pedal monitor
        start_noncrit_component(cjoy.PedalMonitorComponent(window_length=1000))

        # startup the joystick monitor
        start_noncrit_component(cjoy.JoystickMonitorComponent(self.joystick_name))

        # check if noncritical error occurred
        if self.input_noncrit_fail:
            return

        self.default_input()
        return

    def ready_enter(self):
        # Process CMD messages
        self.process_cmd_message()

        # Process UDP CAN is done asynchronously in different components

        # Check driver activity
        self.check_driver_activity()

        # System health check
        self.system_health_check()
