"""
Project: SSITH CyberPhysical Demonstrator
director.py
Author: Ethan Lew <elew@galois.com>
Date: 06/09/2021
Python 3.8.3
O/S: Windows 10

Kiosk State Machine
Hacker Kiosk backend

Exchange format:
{
    func: "name-of-the-function-to-be-called",
    args: {"dictionary of arguments}
    resp: {"dictionary of return vaues}
    status: response status
        200 -OK
        500 - unexpected failure
        501 - func not implemented
}
"""
import cyberphyslib.kiosk.client as kclient
import cyberphyslib.canlib as canlib
from can import Message
from transitions.extensions import GraphMachine as Machine
from transitions import State
import threading
import zmq
import struct

def page(f):
    """decorator for page action methods"""
    def inner(*args, **kwargs):
        """TODO: make this log instead of print"""
        print(f">>>STATE: {f.__name__}")
        return f(*args, **kwargs)
    return inner

ComponentDictionary = {
    canlib.SCENARIO_BASELINE: "SCENARIO_BASELINE",
    canlib.SCENARIO_SECURE_ECU: "SCENARIO_SECURE_ECU",
    canlib.SCENARIO_SECURE_INFOTAINMENT: "SCENARIO_SECURE_INFOTAINMENT",
    canlib.BESSPIN_TOOL: "BESSPIN_TOOL",
    canlib.TARGET_1: "TARGET_1",
    canlib.TARGET_2: "TARGET_2",
    canlib.TARGET_3: "TARGET_3",
    canlib.TARGET_4: "TARGET_4",
    canlib.TARGET_5: "TARGET_5",
    canlib.TARGET_6: "TARGET_6",
    canlib.TEENSY: "TEENSY",
    canlib.IGNITION: "IGNITION",
    canlib.LED_COMPONENT: "LED_COMPONENT",
    canlib.HACKER_KIOSK: "HACKER_KIOSK",
    canlib.HACK_NONE: "HACK_NONE",
    canlib.HACK_OTA: "HACK_OTA",
    canlib.HACK_BRAKE: "HACK_BRAKE",
    canlib.HACK_THROTTLE: "HACK_THROTTLE",
    canlib.HACK_TRANSMISSION: "HACK_TRANSMISSION",
    canlib.HACK_LKAS: "HACK_LKAS",
    canlib.HACK_INFOTAINMENT_1: "HACK_INFOTAINMENT_1",
    canlib.HACK_INFOTAINMENT_2: "HACK_INFOTAINMENT_2",
    canlib.INFOTAINMENT_THIN_CLIENT: "INFOTAINMENT_THIN_CLIENT",
    canlib.INFOTAINMENT_SERVER_1: "INFOTAINMENT_SERVER_1",
    canlib.INFOTAINMENT_SERVER_2: "INFOTAINMENT_SERVER_2",
    canlib.INFOTAINMENT_SERVER_3: "INFOTAINMENT_SERVER_3",
}


class HackerKiosk:
    """
    Kiosk Director implements the desired state flow for the hacker kiosk experience
    """
    ZMQ_PORT = 5091
    ZMQ_POLL_TIMEOUT = 0.1
    OTA_SERVER_IP = {
        canlib.SCENARIO_BASELINE: "10.88.88.11",
        canlib.SCENARIO_SECURE_INFOTAINMENT: "10.88.88.21",
        canlib.SCENARIO_SECURE_ECU: "10.88.88.31",
    }

    # full name of the states
    state_names = [
                   "reset",
                   "hack02_kiosk_intro",
                   "hack05_info_attempt",
                   "hack06_info_exploit",
                   "hack06_info_exploit_attemp_hack",
                   "hack08_critical_exploit",
                   "hack09_protect",
                   "hack10_protect_info_attempt",
                   "hack10_info_exploit_attempt_hack",
                   "hack12_protect_critical",
                   "hack12_critical_exploit"
                   ]

    # this is a brief description of the state transitions that is expanded at runtime
    # into pytransitions transitions
    transition_names = [
        {'transition': ('reset', 'reset'), 'conditions': 'button_pressed_reset'},
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

    def __init__(self, net_conf, deploy_mode=False):
        """kiosk state machine"""
        assert(net_conf)
        self.deploy_mode = deploy_mode

        self.states = None
        self.transitions = None
        self.inputs = None
        self.machine = self.prepare_state_machine()
        self.state_arg = None
        self.is_reset_completed = False

        self.stop_evt = threading.Event()

        # ZMQ init
        self.zmq_port = net_conf.port_network_ipcPort
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.zmq_port}")

        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)

        # State machine data
        self.active_scenario = canlib.SCENARIO_BASELINE
        self.ota_server_port = net_conf.port_network_otaServerPort
        self.brakes_ok = True
        self.lkas_ok = True
        self.transmission_ok = True
        self.throttle_ok = True
        self.hack12_has_been_initialized = False

        # IPC message
        self.ipc_msg = {}

        if self.deploy_mode:
            # CMD BUS
            cmd_host, cmd_subscribers = net_conf.getCmdNetworkNodes("HackerKiosk")
            self.cmd_bus = canlib.TcpBus(cmd_host, cmd_subscribers)
            # CAN UDP BUS (For hacked infotainment server)
            self.can_bus = canlib.CanUdpNetwork("kiosk-udp-can", port=net_conf.port_network_canbusPort,
                                                    ip=net_conf.nodes['HackerKiosk'],
                                                    whitelist=["10.88.88.11"],
                                                    do_bind=True)
            self.cmd_thread = threading.Thread(target=self.cmdLoop, args=[], daemon=True)

        print(f"<{self.__class__.__name__}> Listening on ZMQ_PORT {self.zmq_port}")
        self.default_inputs()

    def run(self):
        while not self.stopped:
            msgs = dict(self.poller.poll(HackerKiosk.ZMQ_POLL_TIMEOUT))
            if self.socket in msgs and msgs[self.socket] == zmq.POLLIN:
                req = self.socket.recv_json()
                print(f"<{self.__class__.__name__}> Got request: {req}")
                self.ipc_msg['args'] = req['args']
                self.ipc_msg['func'] = req['func']
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

    def cmdLoop(self):
        while True:
            msg = self.cmd_bus.recv()
            if msg:
                cid, data = msg.arbitration_id, msg.data
                try:
                    # TODO?
                    print(f"<{self.__class__.__name__}> CAN_ID={cid}, data={data}")
                except Exception as exc:
                    print(f"<{self.__class__.__name__}> Error processing message: {msg}: {exc}")

    @property
    def is_finished(self):
        """state machine termination condition"""
        return False

    def default_inputs(self):
        """set all button inputs to false"""
        for inp in self.inputs:
            setattr(self, f'{inp}', False)

    def resetEcuState(self):
        self.brakes_ok = True
        self.lkas_ok = True
        self.transmission_ok = True
        self.throttle_ok = True

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

        TODO: Reset Targets if needed
        """
        self.button_pressed_next = False
        self.button_pressed_reset = False

        # TODO: reqquest Target1 reset (and infotainment on target 1 and target 3)
        self.hackActive(canlib.HACK_NONE)
        self.switchActiveScenario(canlib.SCENARIO_BASELINE)

        self.hack12_has_been_initialized = False

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
        Hack OTA server
        """
        self.button_pressed_next = False

        if self.deploy_mode:
            hack_ok, data = self.ota_server.hack_server()
            print(data)
        else:
            print("Attemptig to hack OTA server.")
            print("Hack successful!")
            hack_ok = True

        self.ipc_msg['retval'] = hack_ok
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

        self.execute_infotainment_hack(arg)

        self.ipc_msg['status'] = 200 # OK


    @page
    def hack08_critical_exploit_enter(self, arg):
        """
        Attemp a selected critical exploit

        TODO: check args for which hack to use
        """
        self.button_pressed_critical_exploit = False
        self.exploit_complete = True

        self.execute_ecu_hack(arg)

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack09_protect_enter(self, arg):
        """
        Switch to SSITH_INFOTAINMENT_SCENARIO
        Reset baseline target(s)?
        """
        self.button_pressed_next = False

        self.hackActive(canlib.HACK_NONE)
        self.switchActiveScenario(canlib.SCENARIO_SECURE_INFOTAINMENT)

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack10_protect_info_attempt_enter(self, arg):
        """
        Attempt OTA hack
        """
        self.button_pressed_ssith_infotainment = False

        if self.deploy_mode:
            hack_ok, data = self.ota_server.hack_server()
            print(data)
        else:
            print("Attemptig to hack OTA server.")
            print("Hack failed!")
            hack_ok = False

        self.ipc_msg['retval'] = hack_ok
        self.ipc_msg['status'] = 200 # OK

    @page
    def hack10_info_exploit_attempt_hack_enter(self, arg):
        """
        Attemp a selected infotainment exploit

        """
        self.button_pressed_info_exploit = False
        self.exploit_complete = True

        self.execute_infotainment_hack(arg)
        # TODO FXI THIS
        self.ipc_msg['retval'] = "Hack Failed"

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack12_protect_critical_enter(self, arg):
        """
        If active scenario is NOT the SSITH_ECU,
        switch to SSITH_ECU scenario
        """
        self.button_pressed_ssith_ecu = False

        if not self.hack12_has_been_initialized:
            self.switchActiveScenario(canlib.SCENARIO_SECURE_ECU)

            if self.deploy_mode:
                hack_ok, data = self.ota_server.hack_server()
                print(hack_ok)
                print(data)
            else:
                print("Attemptig to hack OTA server.")
                print("Hack succesfull!")

            self.hack12_has_been_initialized = True

        self.ipc_msg['status'] = 200 # OK

    @page
    def hack12_critical_exploit_enter(self, arg):
        """
        Attemp a selected ecu exploit
        """
        self.button_pressed_critical_exploit = False
        self.exploit_complete = True

        self.execute_ecu_hack(arg)
        # TODO FXI THIS
        self.ipc_msg['retval'] = False
        self.ipc_msg['status'] = 200 # OK


    def switchActiveScenario(self, scenario_id) -> bool:
        # Update state
        self.active_scenario = scenario_id

        # Reset internal states
        self.resetEcuState()

        # Set OTA client
        url = f"http://{HackerKiosk.OTA_SERVER_IP[self.active_scenario]}:{self.ota_server_port}"

        print(f"Setting up OTA client with URL: {url}")
        print(f"CMD_CHANGE_ACTIVE_SCENATIO: {ComponentDictionary[scenario_id]}")

        if self.deploy_mode:
            self.ota_server = kclient.HackOtaClient(url)

            try:
                msg = Message(arbitration_id=canlib.CAN_ID_CMD_ACTIVE_SCENARIO,
                            data=struct.pack(canlib.CAN_FORMAT_CMD_ACTIVE_SCENARIO, scenario_id))
                self.cmd_bus.send(msg)
                return True
            except Exception as exc:
                print(f"<{self.__class__.__name__}> Error sending message: {msg}: {exc}")
                return False
        else:
            return True

    def restartComponent(self, component_id) -> bool:
        print(f"CAN_ID_CMD_RESTART: {ComponentDictionary[component_id]}")
        if self.deploy_mode:
            try:
                msg = Message(arbitration_id=canlib.CAN_ID_CMD_RESTART,
                            data=struct.pack(canlib.CAN_FORMAT_CMD_RESTART, component_id))
                self.cmd_bus.send(msg)
                return True
            except Exception as exc:
                print(f"<{self.__class__.__name__}> Error sending message: {msg}: {exc}")
                return False
        else:
            print(f"CAN_ID_CMD_RESTART: {ComponentDictionary[component_id]}")
            return True

    def hackActive(self, hack_id) -> bool:
        print(f"CAN_ID_CMD_HACK_ACTIVE: {ComponentDictionary[hack_id]}")
        if self.deploy_mode:
            try:
                msg = Message(arbitration_id=canlib.CAN_ID_CMD_HACK_ACTIVE,
                            data=struct.pack(canlib.CAN_FORMAT_CMD_HACK_ACTIVE, hack_id))
                self.cmd_bus.send(msg)
                return True
            except Exception as exc:
                print(f"<{self.__class__.__name__}> Error sending message: {msg}: {exc}")
                return False
        else:
            return True

    def execute_infotainment_hack(self, arg):
        self.hackActive(canlib.HACK_INFOTAINMENT_1)
        # TODO if self.deploy_mode:
        if arg == "volumeUp":
            # TODO: proper send
            self.ipc_msg['retval'] = "Volume increased"
        elif arg == "volumeDown":
            # TODO: proper send
            self.ipc_msg['retval'] = "Volume decreased"
        elif arg == "exfil":
            # TODO: proper send
            self.ipc_msg['retval'] = "124 W, 11N"
        elif arg == "changeStation_1":
            # TODO: proper send
            self.ipc_msg['retval'] = 1
            self.ipc_msg['args'] = 'changeStation'
        elif arg == "changeStation_2":
            # TODO: proper send
            self.ipc_msg['retval'] = 2
            self.ipc_msg['args'] = 'changeStation'
        elif arg == "changeStation_3":
            # TODO: proper send
            self.ipc_msg['retval'] = 3
            self.ipc_msg['args'] = 'changeStation'
        else:
            print(f"Unkwon arg: {arg}")
            self.ipc_msg['retval'] = "Error"

    def execute_ecu_hack(self, arg):
        # TODO if self.deploy_mode:
        # TODO" Send HACK ACTIVE
        if arg == "brakes":
            # TODO:upload proper file
            # hack_ok, _ = self.ota_server.upload_and_execute_file(HackerKiosk.brakeOffHackPath)
            # if hack_ok:
            self.brakes_ok = not self.brakes_ok
            self.ipc_msg['retval'] = self.brakes_ok
            if not self.brakes_ok:
                self.hackActive(canlib.HACK_BRAKE)
            else:
                self.hackActive(canlib.HACK_NONE)
        elif arg == "throttle":
            # TODO:upload proper file
            # hack_ok, _ = self.ota_server.upload_and_execute_file(HackerKiosk.brakeOffHackPath)
            # if hack_ok:
            self.throttle_ok = not self.throttle_ok
            self.ipc_msg['retval'] = self.throttle_ok
            if not self.throttle_ok:
                self.hackActive(canlib.HACK_THROTTLE)
            else:
                self.hackActive(canlib.HACK_NONE)
        elif arg == "lkas":
            # TODO:upload proper file
            # hack_ok, _ = self.ota_server.upload_and_execute_file(HackerKiosk.brakeOffHackPath)
            # if hack_ok:
            self.lkas_ok = not self.lkas_ok
            self.ipc_msg['retval'] = self.lkas_ok
            if not self.lkas_ok:
                self.hackActive(canlib.HACK_LKAS)
            else:
                self.hackActive(canlib.HACK_NONE)
        elif arg == "transmission":
            # TODO:upload proper file
            # hack_ok, _ = self.ota_server.upload_and_execute_file(HackerKiosk.brakeOffHackPath)
            # if hack_ok:
            self.transmission_ok = not self.transmission_ok
            self.ipc_msg['retval'] = self.transmission_ok
            if not self.transmission_ok:
                self.hackActive(canlib.HACK_TRANSMISSION)
            else:
                self.hackActive(canlib.HACK_NONE)
        else:
            print(f"Unkwon arg: {arg}")
            self.ipc_msg['retval'] = False