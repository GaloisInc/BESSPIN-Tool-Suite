"""
Project: SSITH CyberPhysical Demonstrator
health.py
Author: Ethan Lew <elew@galois.com>
Date: 08/23/2021
Python 3.8.3
O/S: Windows 10

Component Health Monitoring Objects and Components
"""
from cyberphyslib.canlib import TcpBus
import cyberphyslib.canlib.canspecs as canspecs
import cyberphyslib.demonstrator.component as cycomp


import abc
import collections
import re
import requests
import typing


import fabric
import can
import struct


class HeartbeatMonitor:
    """
    Heartbeat Monitor has 4 capabilities

    * TcpBus heartbeat (1-N communication)
    * UdpBus heartbeat (1-N communication)
    * ssh request check
    * http request check

    TODO: implement tthis
    """
    def ___init__(self):
        pass


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
    def __init__(self, addr: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addr = addr

    @abc.abstractmethod
    def check_response(self, ret: requests.Response) -> bool:
        raise NotImplementedError

    def run_health_test(self) -> bool:
        try:
            ret = requests.get(self.addr)
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
            print(f"Exception {exc} has occurred")
            return False


class OtaMonitor(HttpMonitor):
    """
    Monitor Infotainment Ota Process (via HTTP request)
    """
    def check_response(self, ret: requests.Response) -> bool:
        return ret.status_code == 200


HeartbeatResponseType = typing.Union[None, typing.Tuple[int, int]]


class TcpHeartbeatMonitor(HealthMonitor):
    """
    Heartbeat monitor is responsible for

        1. sending out the heartbeat requests (REQ)
        2. listening for heartbeat acknowledgements (ACK)
        3. determining system health from ACK patterns
    """
    # length of response buffers (time horizon of ACKs)
    maxlen = 5

    @staticmethod
    def form_heartbeat_req_msg(req_number: int):
        """form REQ can packet"""
        msg = can.Message(arbitration_id=canspecs.CAN_ID_HEARTBEAT_REQ,
                          data=struct.pack(canspecs.CAN_FORMAT_HEARTBEAT_REQ, req_number))
        return msg

    def __init__(self, client_ids: typing.Sequence[int], bus: TcpBus):
        self.curr_req_number = 0
        self.tcp_bus = bus
        self.response_buffer: typing.Dict[int, typing.Deque[HeartbeatResponseType]] = {
            c: collections.deque(maxlen=self.maxlen) for c in client_ids
        }

    def submit_response(self, client_id: int, response: HeartbeatResponseType):
        """submit a response from client_id to the ACK buffer"""
        self.response_buffer[client_id].append(response)

    def send_heartbeat_req_msg(self, req_number: int):
        """set REQ can packet over the TCP bus"""
        m = self.form_heartbeat_req_msg(req_number)
        self.tcp_bus.send(m)

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
            mid = len(buff) if len(buff) <= self.maxlen else max(buff)
            d = self.curr_req_number - mid
            if d > self.maxlen:
                print(f"ERROR: Component with ID {cid} Has Failed Heartbeat Health Test!")
                return False
        return True


class TcpHeartbeatClient:
    """
    TcpHeartbeatClient is responsible for handling the heartbeat events that components are expected
    to have to be correctly monitored by TcpHeartbeatMonitor
    """
    def __init__(self, client_id: int, bus: TcpBus):
        self.client_id = client_id
        self.tcp_bus = bus

    def form_heartbeat_ack_msg(self, req_number: int):
        """form ACK can message"""
        msg = can.Message(arbitration_id=canspecs.CAN_ID_HEARTBEAT_ACK,
                          data=struct.pack(canspecs.CAN_FORMAT_HEARTBEAT_ACK, self.client_id, req_number))
        return msg

    def send_heartbeat_ack_msg(self, req_number: int):
        """send teh ACK message over the tcp bus"""
        self.tcp_bus.send(self.form_heartbeat_ack_msg(req_number))

    def recv(self, timeout=1.0):
        return self.tcp_bus.recv(timeout)


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
    def __init__(self, *args, **kwargs):
        super(HeartbeatTaskComponent, self).__init__(*args, **kwargs)
        # poller properties
        # NOTE: should sample period be larger?
        self.heartbeat_thread = cycomp.ThreadExiting(name=f"{self.name}-heartbeat",
                                                     sample_frequency=1 / self.sample_period)
        self.heartbeat_thread.on_poll = self.on_heartbeat_poll
        self.heartbeat_thread.on_start = self.on_heartbeat_start
        self.heartbeat_thread.on_exit = self.on_heartbeat_exit
        self._heartbeat_call_started = False

    def on_start(self):
        super().on_start()
        self.heartbeat_thread.start()

    def on_exit(self):
        self.heartbeat_thread.exit()
        super().exit()

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
        self._heartbeat_client = None

    def register_heartbeat_bus(self, bus: TcpBus, client_id: int):
        """register heartbeat client component with TCP bus and a client identifier"""
        self._heartbeat_client: TcpHeartbeatClient = TcpHeartbeatClient(client_id, bus)

    def on_heartbeat_poll(self, t):
        if self._heartbeat_client is not None:
            r = self._heartbeat_client.recv(1.0)
            while not isinstance(r, can.Message) or r.arbitration_id != canspecs.CAN_ID_HEARTBEAT_REQ:
                r = self._heartbeat_client.recv()
            idx = struct.unpack("!I", r.data)[0]
            self._heartbeat_client.send_heartbeat_ack_msg(idx)


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
    def __init__(self, *args, **kwargs):
        super(HeartbeatMonitorComponent, self).__init__(*args, **kwargs)
        self._heartbeat_monitor = None
        self.n_clients = 0

    def register_heartbeat_bus(self, bus: TcpBus, client_ids):
        """register the monitor on a bus and provide the clients to be monitored"""
        self._heartbeat_monitor: TcpHeartbeatMonitor = TcpHeartbeatMonitor(client_ids, bus)
        self.n_clients = len(client_ids)

    def on_heartbeat_poll(self, t):
        if self._heartbeat_monitor is not None:
            hm: TcpHeartbeatMonitor = self._heartbeat_monitor
            hm.send_req_nodes()
            rets = [self._heartbeat_monitor.tcp_bus.recv(1.0) for _ in range(self.n_clients)]
            rets = [(struct.unpack(canspecs.CAN_FORMAT_HEARTBEAT_ACK, r.data) if r is not None else r) for r in rets]
            for r in rets:
                if r is not None:
                    hm.submit_response(r[0], r[1])
            hm.run_health_test()

    def run_health_test(self) -> bool:
        if self._heartbeat_monitor is not None:
            hm: TcpHeartbeatMonitor = self._heartbeat_monitor
            return hm.run_health_test()

    @property
    def is_healthy(self) -> bool:
        """health property"""
        return self.run_health_test()

    @property
    def is_unhealthy(self) -> bool:
        return not self.is_healthy
