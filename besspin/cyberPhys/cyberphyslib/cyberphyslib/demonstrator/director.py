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
import cyberphyslib.demonstrator.infotainment as infotain
import cyberphyslib.demonstrator.can_out as ccout
import cyberphyslib.demonstrator.component as ccomp
import cyberphyslib.demonstrator.config as cconf
import cyberphyslib.demonstrator.joystick as cjoy
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
    states=[State(name='startup', on_enter='startup_enter'),
            State(name='noncrit_failure', on_enter='noncrit_failure_enter'),
            State(name='ready', on_enter='ready_enter'),
            State(name='terminate', on_enter='terminate_enter'),
            State(name='self_drive', on_enter='self_drive_enter'),
            State(name='restart', on_enter='restart_enter'),
            State(name='timeout', on_enter='timeout_enter'),
            State(name='cc_msg', on_enter='cc_msg_enter'),
            State(name='can', on_enter='can_enter')]

    transitions = [
        # startup logic
        { 'trigger': 'next_state', 'source': 'startup', 'dest': 'noncrit_failure',
          'conditions': 'input_noncrit_fail', 'unless': 'input_component_fail'},
        { 'trigger': 'next_state', 'source': 'startup', 'dest': 'terminate',
          'conditions': 'input_component_fail' },
        { 'trigger': 'next_state', 'source': 'startup', 'dest': 'ready',
          'unless': ['input_component_fail', 'input_noncrit_fail'] },
        { 'trigger': 'next_state', 'source': 'noncrit_failure', 'dest': 'ready'},

        # ready logic
        {'trigger': 'next_state', 'source': 'ready', 'dest': 'ready',
         'unless': ['input_s_timeout', 'input_cc_msg', 'input_can_msg', 'input_self_drive']},
        {'trigger': 'next_state', 'source': 'ready', 'dest': 'self_drive',
         'conditions': 'input_self_drive', 'unless': ['input_cc_msg', 'input_can_msg', 'input_s_timeout']},
        {'trigger': 'next_state', 'source': 'ready', 'dest': 'timeout',
         'conditions': 'input_s_timeout'},
        {'trigger': 'next_state', 'source': 'ready', 'dest': 'cc_msg',
         'conditions': 'input_cc_msg', 'unless': 'input_s_timeout'},
        {'trigger': 'next_state', 'source': 'ready', 'dest': 'can',
         'conditions': 'input_can_msg', 'unless': ['input_cc_msg', 'input_s_timeout']},

        {'trigger': 'next_state', 'source': 'timeout', 'dest': 'restart'},
        {'trigger': 'next_state', 'source': 'restart', 'dest': 'ready'},
        #{'trigger': 'next_state', 'source': 'restart', 'dest': 'terminate'}, # no known failure modes here
        {'trigger': 'next_state', 'source': 'can', 'dest': 'ready'},
        {'trigger': 'next_state', 'source': 'self_drive', 'dest': 'restart'},
        {'trigger': 'next_state', 'source': 'cc_msg', 'dest': 'ready'},
        {'trigger': 'next_state', 'source': 'cc_msg', 'dest': 'restart'}
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
    def from_network_config(cls, net_conf: cconf.DemonstratorNetworkConfig):
        """produce director from the Besspin environment setup file"""
        cmd_host, cmd_subscribers = net_conf.getCmdNetworkNodes("SimPc")
        ip_sim = net_conf.ip_SimPc
        can_port = net_conf.port_network_canbusPort
        info_port = net_conf.port_network_infotainmentUiPort
        return cls(cmd_host, cmd_subscribers, ip_sim, can_port, info_port,
                   ssith_info_whitelist=net_conf.wl_SSITH_INFO_WHITELIST,
                   ssith_ecu_whitelist=net_conf.wl_SSITH_ECU_WHITELIST,
                   base_whitelist=net_conf.wl_BASELINE,
                   apply_lists=cconf.APPLY_LISTS)

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
        self.cc_timeout = cconf.CC_TIMEOUT # 20 seconds

        # Need to know what is the active scenario
        # TODO: is there a better solution?
        self.active_scenario = canlib.SCENARIO_BASELINE

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

        # C&C message bus
        self.cc_recvr = canlib.TcpBus(cmd_host, cmd_nodes)

        # input space as class members
        self.input_noncrit_fail = False
        self.input_component_fail = False
        self.input_can_msg = False
        self.input_cc_msg = False
        self.input_s_timeout = False
        self.input_self_drive = False

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
        self.input_can_msg = False
        self.input_cc_msg = False
        self.input_s_timeout = False
        self.input_self_drive = False

    def draw_graph(self, fname: str):
        """draw a fsm graphviz graph (for documentation, troubleshooting)

        NOTE: you will need to install graphviz (with dot)
        """
        self.machine.get_graph().draw(fname, prog='dot')

    def status_send(self, canid, argument):
        msg = extcan.Message(arbitration_id=canid, dlc=1, data=struct.pack("!B", argument))
        self.cc_recvr.send(msg)

### STATE ENTRY CALLBACKS
    def terminate_enter(self):
        self.status_send(canlib.CAN_ID_CMD_COMPONENT_ERROR, 0x00)
        ignition_logger.debug("Termination State: Enter")
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
                ignition_logger.debug(f"{comp.name} service failed to start ({msg})")
                self.input_noncrit_fail = False
                self.input_component_fail = True
                return False
            return True

        def start_noncrit_component(comp):
            if not start_component(comp):
                ignition_logger.debug(f"{comp.name} service failed to start")
                self.input_noncrit_fail = True
                self.input_component_fail = False
                return False
            self.can_multiverse.register(comp)
            return True

        ignition_logger.debug("Startup State: Enter")
        simulator.Sim.kill_beamng(1)

        # startup beamng
        if not start_component(simulator.Sim()): return

        # startup the multiverse
        if not start_component(ccan.CanMultiverseComponent(self.can_multiverse)): return

        # startup the can location poller
        if not start_component(ccout.CanOutPoller(self.can_multiverse)): return

        # add everything to the can multiverse network
        register_components()

        # startup infotainment proxy
        ui = infotain.InfotainmentUi(self.can_multiverse)
        player = infotain.InfotainmentPlayer(self.info_net)
        if not start_component(ui): return
        if not start_component(player): return
        self.can_multiverse.register(ui)
        self.can_multiverse.register(player)

        # TODO: FIXME: componentize this?
        self.info_net.start()

        # startup led manager
        start_noncrit_component(ledm.LedManagerComponent.for_ignition())

        # startup the speedometer
        start_noncrit_component(speedo.Speedo())

        # startup the pedal monitor
        #start_noncrit_component(cjoy.PedalMonitorComponent())

        # startup the joystick monitor
        #start_noncrit_component(cjoy.JoystickMonitorComponent(self.joystick_name))

        # check if noncritical error occurred
        if self.input_noncrit_fail:
            return

        self.default_input()
        return

    @property
    def self_drive_mode(self):
        """self drive state exists in the sim service -- don't duplicate or invalidate this"""
        # TODO: FIXME: ugly access
        return self._handler["beamng"]._in_autopilot

    def process_cc(self, msg):
        """process cc message
        TODO: FIXME: @michal review this carefully -- not sure how compliant this is with the spec
        """
        import struct
        id, data = msg.arbitration_id, msg.data

        try:
            if id == canlib.CAN_ID_CMD_RESTART:
                ignition_logger.debug(f"process cc: restart")
                dev_id = struct.unpack("!I", msg.data)[0]
                if dev_id == canlib.IGNITION:
                    bsim: simulator.Sim = self._handler["beamng"]
                    bsim.restart_command()

            elif id == canlib.CAN_ID_CMD_HACK_ACTIVE:
                hack_idx = struct.unpack("!B", msg.data)[0]
                ignition_logger.debug(f"process cc: set hack active {hack_idx}")
                # Process HACK_ACTIVE messages only in baseline scenario
                if self.active_scenario == canlib.SCENARIO_BASELINE:
                    if self._noncrit:
                        ignition_logger.debug(f"process cc: not setting led manager as noncritical failure occured")
                    else:
                        lm: ledm.LedManagerComponent = self._handler["ledm"]
                        lm.update_pattern(ledm.LedPatterns(IgnitionDirector.hacks2patterns[hack_idx]))

            elif id == canlib.CAN_ID_CMD_ACTIVE_SCENARIO:
                nmap = {
                    canlib.SCENARIO_BASELINE: "base",
                    canlib.SCENARIO_SECURE_ECU: "secure_ecu",
                    canlib.SCENARIO_SECURE_INFOTAINMENT: "secure_infotainment"}
                scen_idx = struct.unpack("!B", msg.data)[0]
                ignition_logger.debug(f"process cc: active scenario {scen_idx}")
                self.active_scenario = scen_idx
                cm: ccan.CanMultiverseComponent = self._handler["canm"]
                cm.select_network(nmap[scen_idx])
                # Update LED patterns
                lm: ledm.LedManagerComponent = self._handler["ledm"]
                if scen_idx == canlib.SCENARIO_BASELINE:
                    pattern = ledm.LedPatterns.NOMINAL
                else:
                    ledm.LedPatterns.SSITH
                lm.update_pattern(ledm.LedPatterns(pattern))

            elif id == canlib.CAN_ID_CMD_SET_DRIVING_MODE:
                aut_idx = struct.unpack("!B", msg.data)[0]
                ignition_logger.debug(f"process cc: set driving mode {aut_idx}")
                bsim: simulator.Sim = self._handler["beamng"]
                if aut_idx == 0:
                    bsim.disable_autopilot_command()
                else:
                    bsim.enable_autopilot_command()
            else:
                pass
        except Exception as exc:
            ignition_logger.error(f"process cc: error with message {msg}: {exc}")

    def ready_enter(self):
        ignition_logger.debug("Ready state: enter")
        self.status_send(canlib.CAN_ID_CMD_COMPONENT_READY, 0x00)
        scenario_start = time.time()
        while((time.time() - scenario_start) < self.scenario_timeout):
            cc_recv = self.cc_recvr.recv(timeout=self.cc_timeout)
            if cc_recv:
                self.default_input()
                self.input_cc_msg = True
                # process the cc_packet
                self.process_cc(cc_recv)
                return
            else: # CC timeout condition
                # NOTE: if jmonitor has failed assume user input is present
                #activity = self._handler['jmonitor'].is_active or self._handler['pmonitor'].is_active
                activity = True

                # if in self drive mode and activity has occurred, get out
                if activity and self.self_drive_mode:
                    self.default_input()
                    self.input_self_drive = False
                    return
                elif self.self_drive_mode or activity: # do nothing if self drive mode or user activity
                    pass
                else:
                    self.default_input()
                    self.input_self_drive = True
                    return

        self.default_input()
        self.input_s_timeout = True

    def cc_msg_enter(self):
        ignition_logger.debug("cc msg state: enter")
        self.default_input()
        return

    def restart_enter(self):
        ignition_logger.debug("Restart state: enter")
        sim: simulator.Sim = self._handler["beamng"]
        msg = sim.restart_command()
        return

    def noncrit_failure_enter(self):
        ignition_logger.debug("Noncrit_failure state: enter")
        ignition_logger.error("Ignition achieved a noncritical error. Continuing anyway...")
        self.status_send(canlib.CAN_ID_CMD_COMPONENT_ERROR, 0x01)
        self._noncrit = True
        self.default_input()
        return

    def self_drive_enter(self):
        sim: simulator.Sim = self._handler["beamng"]
        msg = sim.enable_autopilot_command()
        self.default_input()

    def timeout_enter(self):
        ignition_logger.info("Timeout state: enter")
        self.default_input()
