#! /usr/bin/env python3

from besspin.base.utils.misc import *
import besspin.cyberPhys.launch
import besspin.cyberPhys.cyberphyslib.cyberphyslib.demonstrator.component as ccomp
import besspin.cyberPhys.cyberphyslib.cyberphyslib.canlib as canlib


from transitions import Machine, State

import time
import struct
import can as extcan

class Commander(ccomp.ComponentPoller):
    """
    TODO FSM
    """
    READY_MSG_TIMEOUT = 10.0 #[s]
    CC_TIMEOUT = 0.1
    POLL_FREQ = 1.0
    # FSM description
    states=[State(name='boot'), # All targets booted OK
            State(name='ready', on_enter='ready_enter'), # Targets are ready
            State(name='restart_target', on_enter='restart_target_enter'), # Restart target
            State(name='failure_recovery', on_enter='failure_recovery_enter'), # Attempt to recovery a failed restart
            State(name='degraded_mode', on_enter='degraded_mode_enter'), # Initialize degraded mode
            State(name='terminate', on_enter='terminate_enter')] # Terminate the tool

    transitions = [
        # startup logic
        { 'trigger': 'next_state', 'source': 'boot', 'dest': 'ready'},

        # ready logic
        {'trigger': 'next_state', 'source': 'ready', 'dest': 'ready',
         'unless': ['target_error, target_reset_requested']},
        {'trigger': 'next_state', 'source': 'ready', 'dest': 'restart_target',
         'conditions': 'target_error'},
        {'trigger': 'next_state', 'source': 'ready', 'dest': 'restart_target',
         'conditions': 'target_reset_requested'},
        {'trigger': 'next_state', 'source': 'restart_target', 'dest': 'ready',
         'conditions': 'restart_ok'},
        {'trigger': 'next_state', 'source': 'restart_target', 'dest': 'failure_recovery',
         'conditions': 'restart_failed'},

        # recovery logic
        {'trigger': 'next_state', 'source': 'failure_recovery', 'dest': 'terminate',
         'unless': 'recovery_possible'},
        {'trigger': 'next_state', 'source': 'failure_recovery', 'dest': 'degraded_mode',
         'conditions': 'recovery_possible'},
        {'trigger': 'next_state', 'source': 'degraded_mode', 'dest': 'ready',
         'conditions': 'degraded_mode_possible'},
        {'trigger': 'next_state', 'source': 'degraded_mode', 'dest': 'terminate',
         'unless': 'degraded_mode_possible'},
    ]

    target_ids = {
        canlib.TEENSY: 0,
        canlib.TARGET_1: 1,
        canlib.TARGET_2: 2,
        canlib.TARGET_3: 3,
        canlib.TARGET_4: 4,
        canlib.TARGET_5: 5,
        canlib.TARGET_6: 6,
    }

    target_list = [canlib.TEENSY, canlib.TARGET_1, canlib.TARGET_2, canlib.TARGET_3, canlib.TARGET_4, canlib.TARGET_5, canlib.TARGET_6]

    def __init__(self):
        # input space as class members
        self.target_reset_requested = False
        self.ready_msg_timeout = False
        self.target_error = False
        self.restart_ok = False
        self.recovery_possible = False
        self.restart_failed = False
        self.degraded_mode_possible = False
        self.machine = Machine(self, states=self.states, transitions=self.transitions, initial='boot')
        self.targets = []
        for _ in range(1,getSetting('nTargets')+1):
            self.targets.append("READY")
        self.last_ready_msg = 0.0

        # C&C Network connection
        host, subscribers = besspin.cyberPhys.launch.getNetworkNodes("AdminPc")
        self.cc_bus = canlib.TcpBus(host, subscribers)

        # Communication with other components
        name = "commander"
        in_socks, out_socks = besspin.cyberPhys.launch.getComponentPorts(name)
        super().__init__(name, in_socks, out_socks, sample_frequency=self.POLL_FREQ)

    def draw_graph(self, fname: str):
        """draw a fsm graphviz graph (for documentation, troubleshooting)

        NOTE: you will need to install graphviz (with dot)
        """
        self.machine.get_graph().draw(fname, prog='dot')

    def on_poll_poll(self, t):
        """poll next state"""
        self.next_state()

    # TODO: handle sending component_id|error_code as required in message specs
    # TODO: add `dlc` into canspecs.py
    def send_component_error(self, component_id):
        msg = extcan.Message(arbitration_id=canlib.CMD_ID_COMPONENT_ERROR,
            dlc=2,
            data=struct.pack(canlib.CMD_FORMAT_COMPONENT_ERROR, component_id))
        self.cc_bus.send(msg)

    def send_component_ready(self, component_id):
        msg = extcan.Message(arbitration_id=canlib.CMD_ID_COMPONENT_READY,
            dlc=1,
            data=struct.pack(canlib.CMD_FORMAT_COMPONENT_READY, component_id))
        self.cc_bus.send(msg)

    def process_cc(self, msg):
        """process cc message
        """
        cid, data = msg.arbitration_id, msg.data

        try:
            if cid == canlib.CAN_ID_CMD_RESTART:
                dev_id = struct.unpack(canlib.CAN_FORMAT_CMD_RESTART, data)[0]
                if dev_id in self.target_ids:
                    targetId = self.target_ids[dev_id]
                    self.targets[targetId] = "RESET"
                    self.target_reset_requested = True
                    
        except Exception as exc:
            printAndLog(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

    def ready_enter(self):
        """
        Most common state
        Check if there is a problem from the watchdog (target restarted)
        TODO: when to reset ALL targets?
        """
        # Periodically send CMD_COMPONENT_READY()
        if (time.time() - self.last_ready_msg) > self.READY_MSG_TIMEOUT:
            self.send_component_ready(canlib.BESSPIN_TOOL)
        
        # Check if there is a C&C restart request (single target)
        cc_recv = self.cc_bus.recv(timeout=self.CC_TIMEOUT)
        if cc_recv:
            self.process_cc(cc_recv)
    
    def restart_target_enter(self):
        """
        Initiate target restart
        """
        printAndLog(f"<{self.__class__.__name__}> Restarting target")
        self.target_reset_requested = False

        for targetId in range(1,getSetting('nTargets')+1):
            if self.targets[targetId] == "RESET":
                # Initiate reset of this target
                self.send_message(ccomp.Message(f"RESET {targetId}"), getSetting('cyberPhysComponentBaseTopic'))
                self.targets[targetId] = "WAIT"

    def failure_recovery_enter(self):
        """
        Not much to do here right now
        TODO: better failure recovery
        """
        printAndLog(f"<{self.__class__.__name__}> Attempting failure recovery...")

    def terminate_enter(self):
        """
        Send CMD_COMPONENT_ERROR before exiting
        NOTE: not sure how well this will fit the flow - maybe replace this
        with a call in __del__ function
        """
        self.send_component_error(canlib.BESSPIN_TOOL)
        printAndLog(f"<{self.__class__.__name__}> Terminating...")

    @recv_topic("base-topic")
    def _(self, msg, t):
        """Filter received messages"""
        for targetId in range(1,getSetting('nTargets')+1):
            if msg == f"READY {targetId}":
                print(msg) # DEBUG
                self.targets[targetId] = "READY"
                self.restart_ok = True
                self.send_component_ready(self.target_list[targetId])
            elif msg == f"ERROR {targetId}":
                print(msg) # DEBUG
                # Request a reset of the target
                self.targets[targetId] = "RESET"
                self.target_reset_requested = True

