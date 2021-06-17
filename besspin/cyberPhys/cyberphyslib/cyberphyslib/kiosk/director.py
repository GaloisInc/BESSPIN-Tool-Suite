"""
Project: SSITH CyberPhysical Demonstrator
director.py
Author: Ethan Lew <elew@galois.com>
Date: 06/09/2021
Python 3.8.3
O/S: Windows 10

Kiosk State Machine
"""
import cyberphyslib.kiosk.client as kclient
import cyberphyslib.kiosk.kiosk as kkiosk
import cyberphyslib.canlib as canlib
from transitions.extensions import GraphMachine as Machine
from transitions import State
import threading
import zmq


def page(f):
    """decorator for page action methods"""
    def inner(*args, **kwargs):
        """TODO: make this log instead of print"""
        print(f">>>STATE: {f.__name__}")
        return f(*args, **kwargs)
    return inner


class HackerKiosk:
    """
    Kiosk Director implements the desired state flow for the hacker kiosk experience
    """

    ZMQ_PORT = 5091
    ZMQ_POLL_TIMEOUT = 0.1

    # full name of the states
    state_names = ["reset",
                   "hack02_kiosk_intro",
                   "hack05_info_attempt",
                   "hack06_info_exploit",
                   "hack06_info_exploit_attemp_hack",
                   "hack08_critical_exploit",
                   "hack09_protect",
                   "hack10_protect_info_attempt",
                   "hack10_info_exploit_attempt_hack",
                   "hack12_protect_critical",
                   "hack12_critical_exploit"]

    # this is a brief description of the state transitions that is expanded at runtime
    # into pytransitions transitions
    transition_names = [
        {'transition': ('reset', 'hack02_kiosk_intro'), 'conditions': 'button_pressed_next'},
        {'transition': ('hack02_kiosk_intro', 'hack05_info_attempt'), 'conditions': 'button_pressed_next'},
        {'transition': ('hack05_info_attempt', 'hack06_info_exploit'), 'conditions': 'button_pressed_next'},
        {'transition': ('hack06_info_exploit', 'hack06_info_exploit_attemp_hack'), 'conditions': 'button_pressed_info_exploit'},
        {'transition': ('hack06_info_exploit_attemp_hack', 'hack06_info_exploit'), 'conditions': 'exploit_complete'},
        {'transition': ('hack06_info_exploit', 'hack08_critical_exploit'), 'conditions': 'button_pressed_critical_exploit'},
        {'transition': ('hack08_critical_exploit', 'hack06_info_exploit'), 'conditions': 'exploit_complete'},
        {'transition': ('hack06_info_exploit', 'hack09_protect'), 'conditions': 'button_pressed_next'},
        {'transition': ('hack09_protect', 'hack10_protect_info_attempt'), 'conditions': 'button_pressed_ssith_infotainment'},
        {'transition': ('hack10_protect_info_attempt', 'hack10_info_exploit_attempt_hack'), 'conditions': 'button_pressed_info_exploit'},
        {'transition': ('hack10_info_exploit_attempt_hack', 'hack10_protect_info_attempt'), 'conditions': 'exploit_complete'},
        {'transition': ('hack09_protect', 'hack12_protect_critical'), 'conditions': 'button_pressed_ssith_ecu'},
        {'transition': ('hack12_protect_critical', 'hack12_critical_exploit'), 'conditions': 'button_pressed_critical_exploit'},
        {'transition': ('hack12_critical_exploit', 'hack12_protect_critical'), 'conditions': 'exploit_complete'},
        {'transition': ('hack02_kiosk_intro', 'reset'), 'conditions': 'button_pressed_reset'},
        {'transition': ('hack05_info_attempt', 'reset'), 'conditions': 'button_pressed_reset'},
        {'transition': ('hack06_info_exploit', 'reset'), 'conditions': 'button_pressed_reset'},
        {'transition': ('hack09_protect', 'reset'), 'conditions': 'button_pressed_reset'},
        {'transition': ('hack10_protect_info_attempt', 'reset'), 'conditions': 'button_pressed_reset'},
        {'transition': ('hack12_protect_critical', 'reset'), 'conditions': 'button_pressed_reset'},
    ]

    @classmethod
    def for_besspin(cls, dnc):
        """argument free constructor"""
        return cls(None, None)

    def __init__(self):
        """kiosk state machine"""
        self.states = None
        self.transitions = None
        self.inputs = None
        self.machine = self.prepare_state_machine()
        self.state_arg = None
        self.is_reset_completed = False

        self.stop_evt = threading.Event()

        # ZMQ init
        self.zmq_port = HackerKiosk.ZMQ_PORT
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.zmq_port}")

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        # IPC message
        self.ipc_msg = {}

        print(f"<{self.__class__.__name__}> Listening on ZMQ_PORT {self.zmq_port}")
        self.default_inputs()

    def run(self):
        while not self.stopped:
            #self.default_inputs()
            msgs = dict(self.poller.poll(HackerKiosk.ZMQ_POLL_TIMEOUT))
            if self.socket in msgs and msgs[self.socket] == zmq.POLLIN:
                req = self.socket.recv_json()
                # print(f"<{self.__class__.__name__}> Got request: {req}")
                self.ipc_msg['args'] = req['args']
                self.ipc_msg['func'] = req['func']
                # resp['retval'] = {}
                # resp['status'] = 200 # OK
                # print(f"<{self.__class__.__name__}> Responding with {resp}")
                # self.socket.send_json(resp)
                self.submit_button(self.ipc_msg['func'],self.ipc_msg['args'])
                self.socket.send_json(self.ipc_msg)
            else:
                self.next_state([])



    def stop(self):
        self.stop_evt.set()

    @property
    def stopped(self):
        return self.stop_evt.is_set()

    def exit(self):
        self.stop()

    def cmd_loop(self):
        while True:
            msg = self.kiosk.canbus.recv()
            if msg:
                self.kiosk.process_cmd_msg(msg)

    @property
    def is_finished(self):
        """state machine termination condition"""
        return False

    def default_inputs(self):
        """set all button inputs to false"""
        for inp in self.inputs:
            setattr(self, f'{inp}', False)


    def submit_button(self, button_name, arg):
        """activate a button input and send the kiosk to the next state"""
        self.default_inputs()
        if hasattr(self, f'button_pressed_{button_name}'):
            setattr(self, f'button_pressed_{button_name}', True)
        else:
            print(f"Error: unknown button: {button_name}")
            pass
        self.next_state(arg)

    def set_arg(self, arg=None):
        """setter for arguments shared between button call and state"""
        self.state_arg = arg

    def prepare_state_machine(self):
        """expand state machine description and create pytransitions machine"""
        # create state objects from state name
        self.states = [State(name=s, on_enter=f'{s}_enter') for s in self.state_names]

        # create transition objects from static transition description
        self.transitions  = []
        self.inputs = set()
        for tn in self.transition_names:
            base_dict = {'trigger': 'next_state',
                         'source': tn['transition'][0],
                         'dest': tn['transition'][1],
                         'before': 'set_arg'}
            if 'conditions' in tn:
                base_dict['conditions'] = tn['conditions']
                self.inputs |= {tn['conditions']}
            if 'unless' in tn:
                base_dict['unless'] = tn['unless']
                self.inputs |= {tn['unless']}
            self.transitions.append(base_dict)

        return Machine(self, states=self.states, transitions=self.transitions, initial='reset', show_conditions=True)


    def draw_graph(self, fname: str):
        """draw a fsm graphviz graph (for documentation, troubleshooting)

        NOTE: you will need to install graphviz (with dot)
        """
        self.machine.get_graph().draw(fname, prog='dot')


    @page
    def reset_enter(self, arg):
        """
        Swith to BASELINE_SCENARIO
        Reset Targets if needed
        """
        self.button_pressed_next = False

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack02_kiosk_intro_enter(self, arg):
        """
        Reset is complete
        No action needed
        """
        self.button_pressed_next = False

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack05_info_attempt_enter(self, arg):
        """
        TODO: Initialize OTA hack
        """
        self.button_pressed_next = False

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack06_info_exploit_enter(self, arg):
        """
        Wait for the exploit selection
        """
        self.button_pressed_next = False
        self.exploit_complete = False

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack06_info_exploit_attemp_hack_enter(self, arg):
        """
        Attemp a selected infotainment exploit

        TODO: check args for which hack to use
        """
        self.button_pressed_info_exploit = False
        self.exploit_complete = True

        self.ipc_msg['status'] = 200 # OK
        self.ipc_msg['retval'] = "HACK OK"

    @page
    def hack08_critical_exploit_enter(self, arg):
        """
        Attemp a selected critical exploit

        TODO: check args for which hack to use
        """
        self.button_pressed_critical_exploit = False
        self.exploit_complete = True

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack09_protect_enter(self, arg):
        """
        Switch to SSITH_INFOTAINMENT_SCENARIO
        Reset baseline target(s)?
        """
        self.button_pressed_next = False

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack10_protect_info_attempt_enter(self, arg):
        """
        TODO: Attempt OTA hack
        """
        self.button_pressed_ssith_infotainment = False

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack10_info_exploit_attempt_hack_enter(self, arg):
        """
        Attemp a selected infotainment exploit

        TODO: check args for which hack to use
        """
        self.button_pressed_info_exploit = False
        self.exploit_complete = True

        self.ipc_msg['status'] = 200 # OK
        self.ipc_msg['retval'] = "Hack Failed"

    @page
    def hack12_protect_critical_enter(self, arg):
        """
        If active scenario is NOT the SSITH_ECU,
        switch to SSITH_ECU scenario
        """
        self.button_pressed_ssith_ecu = False

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack12_critical_exploit_enter(self, arg):
        """nothing"""
        self.button_pressed_critical_exploit = False
        self.exploit_complete = True
