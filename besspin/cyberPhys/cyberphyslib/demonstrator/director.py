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
import cyberphyslib.demonstrator.config as cconf
from cyberphyslib.demonstrator.handler import ComponentHandler
from cyberphyslib.demonstrator.logger import ignition_logger

#import transitions
from transitions.extensions import GraphMachine as Machine
from transitions import State


class IgnitionDirector:
    """
    main ignition program
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
        { 'trigger': 'startup_fadecandy_fail', 'source': 'startup', 'dest': 'noncrit_failure' },
        { 'trigger': 'startup_component_failed', 'source': 'startup', 'dest': 'terminate' },
        { 'trigger': 'startup_success', 'source': 'startup', 'dest': 'ready' },
        { 'trigger': 'noncrit_finished', 'source': 'noncrit_failure', 'dest': 'ready'},
        {'trigger': 'ready_no_cc', 'source': 'ready', 'dest': 'ready'},
        {'trigger': 'ready_self_drive', 'source': 'ready', 'dest': 'self_drive'},
        {'trigger': 'ready_timeout', 'source': 'ready', 'dest': 'timeout'},
        {'trigger': 'ready_cc_msg', 'source': 'ready', 'dest': 'cc_msg'},
        {'trigger': 'ready_can', 'source': 'ready', 'dest': 'can'},
        {'trigger': 'timeout_restart', 'source': 'timeout', 'dest': 'restart'},
        {'trigger': 'restart_finished', 'source': 'restart', 'dest': 'ready'},
        {'trigger': 'restart_failed', 'source': 'restart', 'dest': 'terminate'},
        {'trigger': 'can_finished', 'source': 'can', 'dest': 'ready'},
        {'trigger': 'self_drive_end', 'source': 'self_drive', 'dest': 'restart'},
        {'trigger': 'cc_msg_finished', 'source': 'cc_msg', 'dest': 'ready'},
        {'trigger': 'cc_msg_restart', 'source': 'cc_msg', 'dest': 'restart'}
    ]

    def __init__(self):
        self.can_multiverse = None
        self.info_net = None
        self.proxy = None

        self._handler = ComponentHandler()
        self.machine = Machine(self, states=self.states, transitions=self.transitions, initial='startup')
        self.startup_enter()

    def terminate_enter(self):
        ignition_logger.debug("Termination State: Enter")
        self._handler.exit()

    def noncrit_failure_enter(self):
        ignition_logger.debug("Noncritical Failure State: Enter")

    def startup_enter(self):
        ignition_logger.debug("Startup State: Enter")

        sip = cconf.SIM_IP
        can_ssith_info = ccan.CanUdpNetwork("secure_infotainment", cconf.CAN_PORT, sip)
        can_ssith_ecu = ccan.CanUdpNetwork("secure_ecu", cconf.CAN_PORT, sip)
        can_base = ccan.CanUdpNetwork("base", cconf.CAN_PORT, sip)
        networks = [can_base, can_ssith_ecu, can_ssith_info]

        can_ssith_info.whitelist = cconf.SSITH_INFO_WHITELIST
        can_ssith_ecu.whitelist = cconf.SSITH_ECU_WHITELIST
        can_base.whitelist = cconf.BASE_WHITELIST
        can_ssith_info.blacklist = cconf.SSITH_INFO_BLACKLIST
        can_ssith_ecu.blacklist = cconf.SSITH_ECU_BLACKLIST
        can_base.blacklist = cconf.BASE_BLACKLIST

        # start the can networks
        self.can_multiverse = ccan.CanMultiverse("multiverse", networks, default_network="base")
        self.info_net = ccan.CanUdpNetwork("info-net", cconf.INFO_UI_PORT, sip)

        # startup beamng
        msg = self._handler.start_component(simulator.Sim())
        if msg != simulator.BeamNgStatus.READY:
            ignition_logger.debug(f"BeamNG Sim service failed to start ({msg})")
            self.startup_component_failed()
            return

        # startup the multiverse
        msg = self._handler.start_component(ccan.CanMultiverseComponent(self.can_multiverse))
        if msg != ccan.CanMultiverseStatus.READY:
            ignition_logger.debug(f"CAN multiverse service failed to start ({msg})")
            self.startup_component_failed()
            return

        # startup infotainment proxy
        self.proxy = infotain.InfotainmentProxy(self.info_net, self.can_multiverse)
        self._handler.start_component(self.proxy.info_ui, wait=False)
        self._handler.start_component(self.proxy.info_player, wait=False)

        # startup the speedometer
        msg = self._handler.start_component(speedo.Speedo())
        if msg != speedo.SpeedoStatus.READY:
            #ignition_logger.debug(f"Speedometer service failed to start ({msg})")
            #self.startup_component_failed()
            #return
            # FIXME: speedometer broken on my machine
            pass

        # startup led manager
        msg = self._handler.start_component(ledm.LedManagerComponent.for_ignition())
        if msg != ledm.LedManagerStatus.READY:
            ignition_logger.debug(f"LED Manager service failed to start ({msg})")
            self.startup_fadecandy_fail()
            return

        # otherwise successful
        self.startup_success()
        return

    def ready_enter(self):
        ignition_logger.debug("Ready state: enter")
        # receive CAN and CC message
        # start a timeout event
        # c&c message event

    def restart_enter(self, n_resets=3):
        ignition_logger.debug("Restart state: enter")
        msg = self._handler.message_component("beamng", simulator.BeamNgCommand.RESTART, do_receive=True)
        if msg != simulator.BeamNgStatus.RESTART_FINISHED:
            ignition_logger.warning(f"BeamNG restart failed ({n_resets})!")
            if n_resets >= 0:
                self.restart_enter(n_resets=n_resets - 1)
            else:
                ignition_logger.warning(f"BeamNG restart failed! Terminating...")
                self.restart_failed()
        self.restart_finished()


    def noncrit_failure_enter(self):
        ignition_logger.debug("Noncrit_failure: enter")
        ignition_logger.error("Ignition achieved a noncritical error. The LED manager failed to start. Continuing anyway...")
        self.noncrit_finished()
        return

    def self_drive_enter(self):
        msg = self._handler.message_component("beamng", simulator.BeamNgCommand.ENABLE_AUTOPILOT, do_receive=True)
        # TODO: conditions to disable autopilot
        self.self_drive_end()

    def draw_graph(self, fname: str):
        """draw a fsm graphviz graph (for documentation, troubleshooting)

        NOTE: you will need to install graphviz (with dot)
        """
        self.machine.get_graph().draw(fname, prog='dot')


if __name__ == "__main__":
    fsm = IgnitionDirector()
    fsm.draw_graph('state_diagram.png')
