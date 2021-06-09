"""
Project: SSITH CyberPhysical Demonstrator
director.py
Author: Ethan Lew <elew@galois.com>
Date: 06/09/2021
Python 3.8.3
O/S: Windows 10

Kiosk State Machine
"""
from transitions.extensions import GraphMachine as Machine
from transitions import State


def slide(f):
    """decorator for slide action methods"""
    def inner(*args, **kwargs):
        """TODO: make this log instead of print"""
        print(f.__name__)
        return f(*args, **kwargs)
    return inner


class KioskDirector:
    """
    Kiosk Director implements the desired state flow for the hacker kiosk experience

    TODO: given the similar interfaces with IgnitionDirector, make a state machine base class?
    """

    # full name of the states
    state_names = ["slide2_kiosk_setup",
                   "slide3_introduction",
                   "slide4",
                   "slide5",
                   "slide6a_hack_ota_server",
                   "slide6b_hack_ota_server",
                   "slide7_infotainment_hacks",
                   "slide9",
                   "slide10_hack_critical_systems",
                   "slide15_ssith_intro",
                   "slide16_secure_infotainment",
                   "slide17",
                   "slide18_secure_ecu",
                   "slide19",
                   "slide20_everything_is_hackable",
                   "slide21_ssith_is_the_solution"]

    # this is a brief description of the state transitions that is expanded at runtime
    # into pytransitions transitions
    transition_names = [
        {'transition': ('slide2', 'slide3'), 'conditions': 'input_timer'},
        {'transition': ('slide3', 'slide4'), 'conditions': 'input_hack_car'},
        {'transition': ('slide4', 'slide5'), 'conditions': 'input_exploit_ota'},
        {'transition': ('slide5', 'slide6a'), 'conditions': 'input_hack_infotainment'},
        {'transition': ('slide6a', 'slide6b'), 'conditions': 'input_infotainment_hacked'},
        {'transition': ('slide6b', 'slide7'), 'conditions': 'input_next'},
        {'transition': ('slide7', 'slide7'), 'conditions': 'input_hack'},
        {'transition': ('slide7', 'slide9'), 'conditions': 'input_next', 'unless': 'input_hack'},
        {'transition': ('slide9', 'slide10'), 'conditions': 'input_next'},
        {'transition': ('slide10', 'slide10'), 'conditions': 'input_hack'},
        {'transition': ('slide10', 'slide15'), 'conditions': 'input_next', 'unless': 'input_hack'},
        {'transition': ('slide15', 'slide16'), 'conditions': 'input_hack_infotainment'},
        {'transition': ('slide15', 'slide18'), 'conditions': 'input_hack_critical', 'unless': 'input_hack_infotainment'},
        {'transition': ('slide16', 'slide16'), 'conditions': 'input_hack'},
        {'transition': ('slide18', 'slide18'), 'conditions': 'input_hack'},
        {'transition': ('slide16', 'slide17'), 'conditions': 'input_next', 'unless': 'input_hack'},
        {'transition': ('slide18', 'slide19'), 'conditions': 'input_next', 'unless': 'input_hack'},
        {'transition': ('slide17', 'slide20'), 'conditions': 'input_next'},
        {'transition': ('slide19', 'slide20'), 'conditions': 'input_next'},
        {'transition': ('slide20', 'slide21'), 'conditions': 'input_restart'},
        {'transition': ('slide21', 'slide3'), 'conditions': 'input_next'}
    ]

    def __init__(self):
        """kiosk state machine"""
        self.states = None
        self.transitions = None
        self.inputs = None
        self.machine = self.prepare_state_machine()

    @property
    def is_finished(self):
        """state machine termination condition"""
        return False

    def default_inputs(self):
        """set all button inputs to false"""
        for inp in self.inputs:
            setattr(self, f'{inp}', False)

    def submit_button(self, button_name):
        """activate a button input and send the kiosk to the next state"""
        self.default_inputs()
        if hasattr(self, f'input_{button_name}'):
            setattr(self, f'input_{button_name}', True)
        else:
            # TODO raise warning
            pass
        self.next_state()

    def prepare_state_machine(self):
        """expand state machine description and create pytransitions machine"""
        def get_full_name(n):
            map = {s.split('_')[0]: s for s in self.state_names}
            return map[n]

        # create state objects from state name
        self.states = [State(name=s, on_enter=f'{s}_enter') for s in self.state_names]

        # create transition objects from static transition description
        self.transitions  = []
        self.inputs = set()
        for tn in self.transition_names:
            base_dict = {'trigger': 'next_state',
                         'source': get_full_name(tn['transition'][0]),
                         'dest': get_full_name(tn['transition'][1])}
            if 'conditions' in tn:
                base_dict['conditions'] = tn['conditions']
                self.inputs |= {tn['conditions']}
            if 'unless' in tn:
                base_dict['unless'] = tn['unless']
                self.inputs |= {tn['unless']}
            self.transitions.append(base_dict)

        return Machine(self, states=self.states, transitions=self.transitions, initial='slide2_kiosk_setup', show_conditions=True)


    def draw_graph(self, fname: str):
        """draw a fsm graphviz graph (for documentation, troubleshooting)

        NOTE: you will need to install graphviz (with dot)
        """
        self.machine.get_graph().draw(fname, prog='dot')

    @slide
    def slide2_kiosk_setup_enter(self):
        """timer choice selected"""
        pass

    @slide
    def slide3_introduction_enter(self):
        """introduction
        1. send TX_CMD_ACTIVE_SCENARIO(BASELINE)
        2. send TX_CMD_HACK_ACTIVE(0x0)
        TODO: restart inactive components?
        """
        pass

    @slide
    def slide4_enter(self):
        """nothing"""
        pass

    @slide
    def slide5_enter(self):
        """nothing"""
        pass

    @slide
    def slide6a_hack_ota_server_enter(self):
        """
        1. hack OTA server
        """
        pass

    @slide
    def slide6b_hack_ota_server_enter(self):
        """
        1. upload OTA payload file
        """
        pass

    @slide
    def slide7_infotainment_hacks_enter(self):
        """infotainment server hacks are calls on the python backend (?)"""
        pass

    @slide
    def slide9_enter(self):
        """
        1. attempt to hack the critical systems?
        """
        pass

    @slide
    def slide10_hack_critical_systems_enter(self):
        """
        1. Send TX_CMD_HACK_ACTIVE(hack-number)
        - select correct precompiled binary
        - color button red / green based on selection
        """
        pass

    @slide
    def slide15_ssith_intro_enter(self):
        """
        1. restart baseline scenario components using CMD_RESTART
        2. Send TX_CMD_ACTIVE_SECNARIO(SCENARIO_SECURE_ECU)
        3. Send TX_CMD_HACK_ACTIVE(0x0)
        """
        pass

    @slide
    def slide16_secure_infotainment_enter(self):
        """
        1. Send TX_CMD_ACTIVE_SCENARIO(SCENARIO_SECURE_INFOTAINMENT)
        - All hacks fail with an error message
        - OTA server crashes on SSITH P2 when a hack is attempted
        """
        pass

    @slide
    def slide17_enter(self):
        """nothing"""
        pass

    @slide
    def slide18_secure_ecu_enter(self):
        """
        1. Send TX_CMD_ACTIVE_SCENARIO(SCENARIO_SECURE_ECU)
        - appropriate precompiled binary is selected
        - will be a short unavailability of the ECU (buttons will indicate that)
        """
        pass

    @slide
    def slide19_enter(self):
        """nothing"""
        pass

    @slide
    def slide20_everything_is_hackable_enter(self):
        """nothign"""
        pass

    @slide
    def slide21_ssith_is_the_solution_enter(self):
        """nothing"""
        pass
