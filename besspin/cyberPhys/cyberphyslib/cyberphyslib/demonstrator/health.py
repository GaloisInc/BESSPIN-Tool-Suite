"""
Project: SSITH CyberPhysical Demonstrator
health.py
Author: Ethan Lew <elew@galois.com>
Date: 08/23/2021
Python 3.8.3
O/S: Windows 10

Component Health Monitoring Objects and Components
"""
from cyberphyslib.canlib import TcpBus, UdpBus
import cyberphyslib.canlib.canspecs as canspecs
import cyberphyslib.canlib.componentids as cids
import cyberphyslib.demonstrator.component as cycomp
import cyberphyslib.demonstrator.can as cycan


import abc
import collections
import re
import requests
import typing
import struct
import socket
import time

import fabric
import can


def ip2int(ip):
    """Convert an IP string to an int"""
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]


class HeartbeatMonitor:
    """
    Heartbeat Monitor has 4 capabilities

    * TcpBus heartbeat (1-N communication)
    * UdpBus heartbeat (1-N communication)
    * ssh request check
    * http request check

    TODO: implement this
    """
    def __init__(self, can_bus: cycan.CanUdpNetwork, cc_bus: cycan.CanTcpNetwork):
        self.can_bus = can_bus
        self.cc_bus = cc_bus

        self.services = {
            "can-display-ui":
                {
                    "user" : "pi",
                    "password": "WelcomeToGalois",
                    "address" : "10.88.88.5",
                    "service_name": "can-ui"
                },
            "hacker-kiosk-ui":
                {
                    "user" : "pi",
                    "password": "WelcomeToGalois",
                    "address" : "10.88.88.3",
                    "service_name": "hacker-ui"
                },
            "infotainment-client-ui":
                {
                    "user" : "pi",
                    "password": "WelcomeToGalois",
                    "address" : "10.88.88.2",
                    "service_name": "infotainment"
                }
                    }

        self.https = {
            "ota_server_1" : "http://10.88.88.11:5050",
            "ota_server_2" : "http://10.88.88.21:5050",
            "ota_server_3" : "http://10.88.88.31:5050"
        }

        self.monitor = {"10.88.88.4": cids.IGNITION}
        self.udp_descr = {
            "10.88.88.12": ip2int('10.88.88.11'),
            "10.88.88.22": ip2int('10.88.88.21'),
            "10.88.88.32": ip2int('10.88.88.31'),
            "22.88.88.10": ip2int('22.88.88.10'),
            "32.88.88.10": ip2int('32.88.88.10'),
            "12.88.88.10": ip2int('12.88.88.10'),
        }

        self.tcp_descr = {
            '10.88.88.6:5041': 0x28, # BESSPIN TOOL DEBIAN
            '10.88.88.2:5041': 0x60, # INFOTAINMENT THIN CLIENT
        }

        self.component_monitor = HeartbeatMonitorComponent("can_monitor", set(), set())
        self.ota_monitors = {k: OtaMonitor(addr) for k, addr in self.https.items()}
        self.service_monitors = {k: ServiceMonitor(params["service_name"], params["address"],
                                                   user=params["user"],
                                                   password=params["password"]) for k, params in self.services.items()}

    def mainloop(self):
        import time
        while True:
            time.sleep(1.0)

            print("Testing OTA")
            for k, v in self.ota_monitors.items():
                if not v.is_healthy:
                    print(f"WARNING! {k} HTTP failed health check")

            print("Testing Services")
            for k, v in self.service_monitors.items():
                if not v.is_healthy:
                    print(f"WARNING! {k} Service failed health check")

            print("Testing UDP")
            if self.component_monitor is not None:
                if not self.component_monitor._heartbeat_monitor_udp.is_healthy:
                    print(f"ERROR! UDP Failed")
                print("Testing TCP")
                if not self.component_monitor._heartbeat_monitor_tcp.is_healthy:
                    print(f"ERROR! TCP Failed")

    def setup_can(self):
        """register the UDP CAN bus for the monitoring"""
        self.can_bus.register(self.component_monitor)
        self.component_monitor.register_can_heartbeat_bus(self.can_bus.bus, self.udp_descr.values())

    def setup_cc(self):
        """register the TCP C&C bus for the monitoring"""
        self.cc_bus.register(self.component_monitor)
        self.component_monitor.register_heartbeat_bus(self.cc_bus.bus, self.tcp_descr.values())

    def setup_tcp(self):
        """FIXME: this is no longer relevant as a TCP network object was created"""
        addrs, vals = list(zip(*((k, v) for k,v in self.tcp_descr)))
        self.component_monitor.register_heartbeat_bus(TcpBus(
            list(self.monitor.keys())[0],
            addrs),
            vals
        )

    def start_monitor(self):
        """monitor initialization"""
        self.component_monitor.start()

    def exit_monitor(self):
        """monitor teardown"""
        self.component_monitor.exit()
        self.component_monitor.join()


class HealthMonitor(abc.ABC):
    """Health Monitor Interface

    Define test interface and health properties
    """
    @abc.abstractmethod
    def run_health_test(self) -> bool:
        """test to determine if the system monitored is healthy"""
        return True

    @property
    def is_healthy(self) -> bool:
        """health property"""
        return self.run_health_test()

    @property
    def is_unhealthy(self) -> bool:
        return not self.is_healthy


class SshMonitor(HealthMonitor):
    """
    Health monitoring involving Ssh Connections
    """
    def __init__(self, addr: str, user=None, password=None, **kwargs):
        # user and password need to be transformed into proper level of fabric
        # kwarg hierarchy
        if user:
            kwargs["user"] = user
        if password:
            if "connect_kwargs" in kwargs:
                kwargs["connect_kwargs"] = {**{"password": password}, **kwargs}
            else:
                kwargs["connect_kwargs"] = {"password": password}
        self.connection_kwargs = kwargs
        self.addr: str = addr

    def command(self, command: str):
        # NOTE: should I persist the connect rather than make a new one each time?
        result = fabric.Connection(self.addr, **self.connection_kwargs).run(command, hide=True)
        return result


class HttpMonitor(HealthMonitor):
    """
    Health monitoring involving http connections
    """
    request_timeout = 1.0

    def __init__(self, addr: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addr = addr

    @abc.abstractmethod
    def check_response(self, ret: requests.Response) -> bool:
        raise NotImplementedError

    def run_health_test(self) -> bool:
        try:
            ret = requests.get(self.addr, timeout = self.request_timeout)
            # check for OK status code
            return self.check_response(ret)
        except Exception as exc:
            # TODO: log this?
            return False


class ServiceMonitor(SshMonitor):
    """
    Health monitoring of a service on a remote machine (via Ssh)
    """
    def __init__(self, service_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_name = service_name

    def run_health_test(self) -> bool:
        try:
            ret = self.command(rf"systemctl status {self.service_name}")
            # regex match for active and running service
            # NOTE: is this correct and stable?
            return re.search(r"(Active: active \(running\))", ret.stdout) is not None
        except Exception as exc:
            # TODO: log this?
            #print(f"Exception {exc} has occurred")
            return False


class OtaMonitor(HttpMonitor):
    """
    Monitor Infotainment Ota Process (via HTTP request)
    """
    def check_response(self, ret: requests.Response) -> bool:
        return ret.status_code == 200


HeartbeatResponseType = float


class BusHeartbeatMonitor(HealthMonitor):
    """
    Heartbeat monitor is responsible for

        1. sending out the heartbeat requests (REQ)
        2. listening for heartbeat acknowledgements (ACK)
        3. determining system health from ACK patterns
    """
    # length of response buffers (time horizon of ACKs)
    maxlen = 5
    wait_period = 10.0

    @staticmethod
    def form_heartbeat_req_msg(req_number: int):
        """form REQ can packet"""
        msg = can.Message(arbitration_id=canspecs.CAN_ID_HEARTBEAT_REQ,
                          data=struct.pack(canspecs.CAN_FORMAT_HEARTBEAT_REQ, req_number))
        return msg

    def __init__(self, client_ids: typing.Sequence[int], bus: typing.Union[TcpBus, UdpBus]):
        self.curr_req_number = 0
        self.bus = bus
        self.response_buffer: typing.Dict[int, typing.Deque[HeartbeatResponseType]] = {
            c: collections.deque(maxlen=self.maxlen) for c in client_ids
        }
        self.start_time = time.time()

    def submit_response(self, client_id: int, response: HeartbeatResponseType):
        """submit a response from client_id to the ACK buffer"""
        if client_id not in self.response_buffer:
            idmap = {v: k for k, v in cids.__dict__.items() if isinstance(v, int)}
            cname = idmap.get(client_id, "<UNKNOWN>")
            print(f"WARNING! Received unanticipated response {client_id} ({cname})")
        else:
            #print(f"Submitted {socket.inet_ntoa(struct.pack('!L', client_id))} {response}")
            if response is not None:
                self.response_buffer[client_id].append(time.time())

    def send_heartbeat_req_msg(self, req_number: int):
        """set REQ can packet over the TCP bus"""
        m = self.form_heartbeat_req_msg(req_number)
        self.bus.send(m)

    def send_req_nodes(self):
        """send REQ to nodes"""
        self.send_heartbeat_req_msg(self.curr_req_number)
        self.curr_req_number += 1

    def run_health_test(self) -> bool:
        """implement the heartbeat health:
            for a given history of component with component id cid, if the maximum value is
            within MAXLEN of the current REQ number, the component is considered healthy
        """
        for cid, buff in self.response_buffer.items():
            if len(buff) > 0:
                ltime = max(buff)
                delta = time.time() - ltime
                #print(delta)
                if delta > self.maxlen:
                    print(f"ERROR: Component with ID {cid} Has Failed Heartbeat Health Test!")
                    return False
            else:
                if time.time() - self.start_time > self.wait_period:
                    print(f"ERROR: Component with ID {cid} Has Failed Heartbeat Health Test!")
                    return False
        return True


class BusHeartbeatClient:
    """
    TcpHeartbeatClient is responsible for handling the heartbeat events that components are expected
    to have to be correctly monitored by TcpHeartbeatMonitor
    """
    def __init__(self, client_id: int, bus: typing.Union[TcpBus, UdpBus]):
        self.client_id = client_id
        self.bus = bus

    def form_heartbeat_ack_msg(self, req_number: int):
        """form ACK can message"""
        msg = can.Message(arbitration_id=canspecs.CAN_ID_HEARTBEAT_ACK,
                          data=struct.pack(canspecs.CAN_FORMAT_HEARTBEAT_ACK, self.client_id, req_number))
        return msg

    def send_heartbeat_ack_msg(self, req_number: int):
        """send teh ACK message over the tcp bus"""
        self.bus.send(self.form_heartbeat_ack_msg(req_number))

    def recv(self, timeout=1.0):
        return self.bus.recv(timeout)


class HeartbeatTaskComponent(cycomp.ComponentPoller):
    """
    HeartbeatTaskComponent extends ComponentPoller to have the desired functionality of a heartbeat
    element, hiding implementation from other tasks that the component is responsible for (polling
    task + message handling)

    Examples:
        ```
        myc = heartbeat_component("myc", {("msg-in", 5006)}, {"msg-out", 5007})
        myc.register_heartbeat_bus(bus_obj, [0x45])
        myc.start()
        ```
    """
    def __init__(self, *args, heartbeat_sample_period=0.2, **kwargs):
        super(HeartbeatTaskComponent, self).__init__(*args, **kwargs)
        # poller properties
        # NOTE: should sample period be larger?
        self.heartbeat_thread = cycomp.ThreadExiting(name=f"{self.name}-heartbeat",
                                                     sample_frequency=1 / heartbeat_sample_period)
        self.heartbeat_thread.on_poll = self.on_heartbeat_poll
        self.heartbeat_thread.on_start = self.on_heartbeat_start
        self.heartbeat_thread.on_exit = self.on_heartbeat_exit
        self._heartbeat_call_started = False

    def on_start(self):
        if not self._heartbeat_call_started:
            self.heartbeat_thread.start()
        super().on_start()

    def on_exit(self):
        super().exit()
        if self._heartbeat_call_started:
            self.heartbeat_thread.exit()

    def on_heartbeat_start(self):
        pass

    def on_heartbeat_exit(self):
        pass

    def on_heartbeat_poll(self, t):
        pass


class HeartbeatClientComponent(HeartbeatTaskComponent):
    """
    Heartbeat Client (component to be monitored)

    Examples:
        ```
        myc = heartbeat_component("myc", {("msg-in", 5006)}, {"msg-out", 5007})
        my_id = 0x45
        myc.register_heartbeat_bus(bus_obj, my_id)
        myc.start()
        ```
    """

    def __init__(self, *args, **kwargs):
        super(HeartbeatClientComponent, self).__init__(*args, **kwargs)
        self._heartbeat_client_tcp = None
        self._heartbeat_client_udp = None

    def register_heartbeat_bus(self, bus: TcpBus, client_id: int):
        """register heartbeat client component with TCP bus and a client identifier"""
        self._heartbeat_client_tcp: BusHeartbeatClient = BusHeartbeatClient(client_id, bus)

    def register_can_heartbeat_bus(self, bus: UdpBus, client_id: int):
        self._heartbeat_client_udp: BusHeartbeatClient = BusHeartbeatClient(client_id, bus)

    def on_heartbeat_poll(self, t):
        if self._heartbeat_client_tcp is not None:
            r = self._heartbeat_client_tcp.recv(1.0)
            while not isinstance(r, can.Message) or r.arbitration_id != canspecs.CAN_ID_HEARTBEAT_REQ:
                r = self._heartbeat_client_tcp.recv()
            idx = struct.unpack("!I", r.data)[0]
            self._heartbeat_client_tcp.send_heartbeat_ack_msg(idx)

    @recv_can(canspecs.CAN_ID_HEARTBEAT_REQ, canspecs.CAN_FORMAT_HEARTBEAT_REQ)
    def _(self, data):
        # TODO: check this
        if self._heartbeat_client_udp is not None:
            self._heartbeat_client_udp.send_heartbeat_ack_msg(data[0])

    def recv_cc(self, can_id, data_len, data):
        # unpack
        print("NotImplementedError: recv cc")
        req_number = struct.unpack(canspecs.CAN_FORMAT_HEARTBEAT_REQ, data)
        if self._heartbeat_client_tcp is not None:
            self._heartbeat_client_tcp.send_heartbeat_ack_msg(req_number[0])


class HeartbeatMonitorComponent(HeartbeatTaskComponent):
    """
    Heartbeat Monitor Component (component to check the health of the clients)

    FIXME: all clients must be registered or else the monitor wont receive at the correct rate

    Examples:
        ```
        myc = heartbeat_component("myc", {("msg-in", 5006)}, {"msg-out", 5007})
        client_ids = [0x45, 0x56]
        myc.register_heartbeat_bus(bus_obj, client_ids)
        myc.start()
        ```
    """
    def __init__(self, *args, tcp_timeout=1.0, **kwargs):
        super(HeartbeatMonitorComponent, self).__init__(*args, **kwargs)
        self._heartbeat_monitor_tcp: typing.Optional[BusHeartbeatMonitor] = None
        self._heartbeat_monitor_udp: typing.Optional[BusHeartbeatMonitor] = None
        self.n_clients_tcp = 0
        self.tcp_timeout = tcp_timeout

    def register_heartbeat_bus(self, bus: TcpBus, client_ids):
        """register the monitor on a bus and provide the clients to be monitored"""
        self._heartbeat_monitor_tcp: BusHeartbeatMonitor = BusHeartbeatMonitor(client_ids, bus)
        self.n_clients_tcp = len(client_ids)

    def register_can_heartbeat_bus(self, bus: UdpBus, client_ids):
        self._heartbeat_monitor_udp: BusHeartbeatMonitor = BusHeartbeatMonitor(client_ids, bus)

    def on_heartbeat_poll(self, t):
        if self._heartbeat_monitor_tcp is not None:
            hm: BusHeartbeatMonitor = self._heartbeat_monitor_tcp
            hm.send_req_nodes()
            #rets = [self._heartbeat_monitor_tcp.bus.recv(self.tcp_timeout) for _ in range(self.n_clients_tcp)]
            #rets = [(struct.unpack(canspecs.CAN_FORMAT_HEARTBEAT_ACK, r.data) if r is not None else r) for r in rets]
            #for r in rets:
            #    if r is not None:
            #        hm.submit_response(r[0], r[1])
            #hm.run_health_test()
        if self._heartbeat_monitor_udp is not None:
            hm: BusHeartbeatMonitor = self._heartbeat_monitor_udp
            hm.send_req_nodes()

    def run_health_test(self) -> bool:
        tcp_result = True
        udp_result = True
        if self._heartbeat_monitor_tcp is not None:
            hm: BusHeartbeatMonitor = self._heartbeat_monitor_tcp
            tcp_result = hm.run_health_test()
        if self._heartbeat_monitor_udp is not None:
            hm: BusHeartbeatMonitor = self._heartbeat_monitor_udp
            udp_result = hm.run_health_test()
        return tcp_result and udp_result

    @property
    def is_healthy(self) -> bool:
        """health property"""
        return self.run_health_test()

    @property
    def is_unhealthy(self) -> bool:
        return not self.is_healthy

    @recv_can(canspecs.CAN_ID_HEARTBEAT_ACK, canspecs.CAN_FORMAT_HEARTBEAT_ACK)
    def _(self, data):
        """UDP Acknowledge: submit the ack to the monitor"""
        # TODO: check this
        cid, rnum = data
        if self._heartbeat_monitor_udp is not None:
            self._heartbeat_monitor_udp.submit_response(cid, (cid, rnum))

    def recv_cc(self, can_id, data_len, data):
        """TCP Acknowledge: submit the ack to the monitor"""
        # unpack
        # TODO: test this and remove the print statement
        if can_id == canspecs.CAN_ID_HEARTBEAT_ACK:
            cid, rnum = struct.unpack(canspecs.CAN_FORMAT_HEARTBEAT_ACK, data)
            if self._heartbeat_monitor_tcp is not None:
                self._heartbeat_monitor_tcp.submit_response(cid, (cid, rnum))
