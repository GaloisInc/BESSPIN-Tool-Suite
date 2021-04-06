"""
Project: SSITH CyberPhysical Demonstrator
director.py
Author: Ethan Lew <elew@galois.com>
Date: 04/05/2021
Python 3.8.3
O/S: Windows 10

Interface to manage ignition components
"""
#import transitions
import cyberphyslib.demonstrator.can as ccan
import cyberphyslib.demonstrator.simulator as simulator
import cyberphyslib.demonstrator.speedometer as speedo
from component_tester import ComponentHandler
from transitions.extensions import GraphMachine as Machine
from transitions import State


class IgnitionDirector:
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
        {'trigger': 'can_finished', 'source': 'can', 'dest': 'ready'},
        {'trigger': 'self_drive_end', 'source': 'self_drive', 'dest': 'restart'},
        {'trigger': 'cc_msg_finished', 'source': 'cc_msg', 'dest': 'ready'},
        {'trigger': 'cc_msg_restart', 'source': 'cc_msg', 'dest': 'restart'}
    ]

    def __init__(self):
        self._handler = ComponentHandler()
        self.machine = Machine(self, states=self.states, transitions=self.transitions, initial='startup')
        self.startup_enter()

    def terminate_enter(self):
        print("TERMINATION ENTERED!")
        self._handler.exit()

    def noncrit_failure_enter(self):
        print("noncrit enter")

    def startup_enter(self):
        print('startup_enter')

        # startup beamng
        msg = self._handler.start_component(simulator.Sim)
        if msg != simulator.BeamNgStatus.READY:
            self.startup_component_failed()
            return

        # startup the speedometer
        msg = self._handler.start_component(speedo.Speedo)
        if msg != speedo.SpeedoStatus.READY:
            self.startup_component_failed()
            return

        # startup the multiverse
        msg = self._handler.start_component(ccan.CanMultiverseComponent)
        if msg != ccan.CanMultiverseStatus.READY:
            self.startup_component_failed()
            return

        # otherwise successful
        self.startup_success()
        return

    def ready_enter(self):
        print("READY ENTERED")
        # receive CAN and CC message
        # start a timeout event
        # c&c message event

    def restart_enter(self, n_resets=3):
        msg = self._handler.message_component("beamng", simulator.BeamNgCommand.RESTART, do_receive=True)
        if msg != simulator.BeamNgStatus.RESTART_FINISHED:
            print("RESTART FAILED")
            if n_resets >= 0:
                self.restart_enter(n_resets=n_resets - 1)
            else:
                # TODO?
                print("TERMINATE")
        self.restart_finished()

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
    #fsm.machine.get_graph().draw('my_state_diagram.png', prog='dot')
