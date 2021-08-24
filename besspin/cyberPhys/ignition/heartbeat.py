import abc
import fabric
import re
import requests
import typing as typ
from cyberphyslib.canlib import TcpBus
import cyberphyslib.canlib.canspecs as canspecs
import cyberphyslib.canlib.componentids as cids
import cyberphyslib.demonstrator.can as cycan
import cyberphyslib.demonstrator.component as cycomp
import can
import struct
# TODO: add this to the requirements


class HeartbeatMonitor:
     """
     Heartbeat Monitor has 4 capabilities

     * TcpBus heartbeat (1-N communication)
     * UdpBus heartbeat (1-N communication)
     * ssh request check
     * http request check
     """
     def ___init__(self):
         pass


class HealthMonitor(abc.ABC):
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
    # for now...
    pass


class ServiceMonitor(SshMonitor):
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
            return False


class OtaMonitor(HttpMonitor):
    def __init__(self, addr: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addr = addr

    def run_health_test(self) -> bool:
        try:
            ret = requests.get(self.addr)
            # check for OK status code
            return ret.status_code == 200
        except Exception as exc:
            # TODO: log this?
            return False


import collections


class TcpHeartbeatMonitor(HealthMonitor):
    maxlen = 5

    def __init__(self, client_ids, bus: TcpBus):
        self.curr_req_number = 0
        self.tcp_bus = bus
        self.response_buffer = {c: collections.deque(maxlen=self.maxlen) for c in client_ids}

    def submit_response(self, cid: int, rep):
        self.response_buffer[cid].append(rep)

    def form_heartbeat_req_msg(self, req_number: int):
        msg = can.Message(arbitration_id=canspecs.CAN_ID_HEARTBEAT_REQ,
                          data=struct.pack(canspecs.CAN_FORMAT_HEARTBEAT_REQ, req_number))
        return msg

    def send_heartbeat_req_msg(self, req_number: int):
        m = self.form_heartbeat_req_msg(req_number)
        self.tcp_bus.send(m)

    def send_req_nodes(self):
        #for _, _ in self.id_map.items():
        self.send_heartbeat_req_msg(self.curr_req_number)
        self.curr_req_number += 1

    def main_loop(self):
        while True:
            self.send_req_nodes()
            r = self.tcp_bus.recv(1.0)
            print(r)

    def run_health_test(self) -> bool:
        for cid, buff in self.response_buffer.items():
            mid = len(buff) if len(buff) <= self.maxlen else max(buff)
            d = self.curr_req_number - mid
            if d > self.maxlen:
                print(f"ERROR: Component with ID {cid} Has Failed Heartbeat Health Test!")
                return False
        return True


class TcpHeartbeatClient:
    def __init__(self, client_id: int, bus: TcpBus):
        self.client_id = client_id
        self.tcp_bus = bus

    def form_heartbeat_ack_msg(self, req_number: int):
        msg = can.Message(arbitration_id=canspecs.CAN_ID_HEARTBEAT_ACK,
                          data=struct.pack(canspecs.CAN_FORMAT_HEARTBEAT_ACK, self.client_id, req_number))
        return msg

    def send_heartbeat_ack_msg(self, req_number: int):
        self.tcp_bus.send(self.form_heartbeat_ack_msg(req_number))

    def recv(self, timeout=1.0):
        return self.tcp_bus.recv(timeout)


class HeartbeatTaskComponent(cycomp.ComponentPoller):
    def __init__(self, *args, **kwargs):
        super(HeartbeatTaskComponent, self).__init__(*args, **kwargs)
        # poller properties
        self.heartbeat_thread = cycomp.ThreadExiting(name=f"{self.name}-heartbeat",
                                                   sample_frequency=1 / self.sample_period)
        self.heartbeat_thread.on_poll = self.on_heartbeat_poll
        self.heartbeat_thread.on_start = self.on_heartbeat_start
        self.heartbeat_thread.on_exit = self.on_heartbeat_exit
        self._heartbeat_call_started = False

    def on_start(self):
        self.heartbeat_thread.start()

    def on_exit(self):
        self.heartbeat_thread.exit()

    def on_heartbeat_start(self):
        pass

    def on_heartbeat_exit(self):
        pass

    def on_heartbeat_poll(self, t):
        pass


class HeartbeatClientComponent(HeartbeatTaskComponent):
    def __init__(self, *args, **kwargs):
        super(HeartbeatClientComponent, self).__init__(*args, **kwargs)
        self._heartbeat_client = None

    def register_heartbeat_bus(self, bus: TcpBus, client_id: int):
        self._heartbeat_client: TcpHeartbeatClient = TcpHeartbeatClient(client_id, bus)

    def on_heartbeat_poll(self, t):
        if self._heartbeat_client is not None:
            r = self._heartbeat_client.recv(1.0)
            while not isinstance(r, can.Message) or r.arbitration_id != canspecs.CAN_ID_HEARTBEAT_REQ:
                r = self._heartbeat_client.recv()
            idx = struct.unpack("!I", r.data)[0]
            self._heartbeat_client.send_heartbeat_ack_msg(idx)


class HeartbeatMonitorComponent(HeartbeatTaskComponent):
    def __init__(self, *args, **kwargs):
        super(HeartbeatMonitorComponent, self).__init__(*args, **kwargs)
        self._heartbeat_monitor = None

    def register_heartbeat_bus(self, bus: TcpBus, client_ids):
        self._heartbeat_monitor: TcpHeartbeatMonitor = TcpHeartbeatMonitor(client_ids, bus)
        self.n = len(client_ids)

    def on_heartbeat_poll(self, t):
        if self._heartbeat_monitor is not None:
            hm: TcpHeartbeatMonitor = self._heartbeat_monitor
            hm.send_req_nodes()
            #print(self._heartbeat_monitor.tcp_bus.recv(1.0))
            rets = [self._heartbeat_monitor.tcp_bus.recv(1.0) for _ in range(self.n)]
            rets = [(struct.unpack(canspecs.CAN_FORMAT_HEARTBEAT_ACK, r.data) if r is not None else r) for r in rets]
            for r in rets:
                if r is not None:
                    hm.submit_response(r[0], r[1])
            hm.run_health_test()
            #print(hm.is_healthy)
            #print(hm.response_buffer)



if __name__ == "__main__":
    sm = ServiceMonitor("docker.service", "192.168.0.161", user="elew", password="elew")
    print(sm.is_healthy)
    om = OtaMonitor("https://www.google.com")
    print(om.is_healthy)

    tcp_descr = {"127.0.0.1:5555": 0x0,
                 "127.0.0.1:5556": cids.HACKER_KIOSK,
                 "127.0.0.1:5557": cids.INFOTAINMENT_SERVER_1,
                 "127.0.0.1:5558": cids.INFOTAINMENT_SERVER_2,
                 "127.0.0.1:5559": cids.INFOTAINMENT_SERVER_3}
    thm = HeartbeatMonitorComponent("monitor", set(), set())
    thm.register_heartbeat_bus(TcpBus("127.0.0.1:5555",
                                      ["127.0.0.1:5556", "127.0.0.1:5557",
                                       "127.0.0.1:5558", "127.0.0.1:5559"]),
                               [cids.HACKER_KIOSK, cids.INFOTAINMENT_SERVER_1,
                                cids.INFOTAINMENT_SERVER_2, cids.INFOTAINMENT_SERVER_3])
    clients = [HeartbeatClientComponent(f"client-{idx}", set(), set()) for idx in range(len(tcp_descr)-1)]
    thm.start()
    thm.start_poller()
    for c, (addr, cid) in zip(clients, ((a, c) for a,c in tcp_descr.items() if c !=0)):
        c.register_heartbeat_bus(TcpBus(addr, ["127.0.0.1:5555"]), cid)
        c.start()
        c.start_poller()

    import time
    time.sleep(10.0)
    clients[-1].exit()
    while True:
        pass
