import abc
import fabric
import re
import requests
import typing as typ
from cyberphyslib.canlib import TcpBus
import cyberphyslib.canlib.canspecs as canspecs
import cyberphyslib.canlib.componentids as cids
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
    def __init__(self, connection: str, user=None, password=None, **kwargs):
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
        self.connection: str = connection

    def command(self, command: str):
        # NOTE: should I persist the connect rather than make a new one each time?
        result = fabric.Connection(self.connection, **self.connection_kwargs).run(command, hide=True)
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


class TcpHeartbeatMonitor(HealthMonitor):
    def __init__(self, addr: str, nodes: typ.Dict[str, int]):
        self.addr = addr
        self.nodes = list(nodes.keys())
        self.id_map = nodes
        print(self.addr, self.nodes)
        self.tcp_bus = TcpBus(self.addr, self.nodes)

    def form_heartbeat_req_msg(self, node_id: int):
        msg = can.Message(arbitration_id=canspecs.CAN_ID_HEARTBEAT_REQ,
                          data=struct.pack(canspecs.CAN_FORMAT_HEARTBEAT_REQ, node_id),
                          dlc=4)
        return msg

    def send_heartbeat_req_msg(self, node_id: int):
        m = self.form_heartbeat_req_msg(node_id)
        self.tcp_bus.send(self.form_heartbeat_req_msg(node_id))

    def send_req_nodes(self):
        for node, nid in self.id_map.items():
            self.send_heartbeat_req_msg(nid)

    def main_loop(self):
        while True:
            self.send_req_nodes()
            r = self.tcp_bus.recv(1.0)
            print(r)

    def run_health_test(self) -> bool:
        return True


class TcpHeartbeatClient:
    def __init__(self, addr: str, client_id: int, nodes: typ.Dict[str, int]):
        self.addr = addr
        self.nodes = list(nodes.keys())
        self.id_map = nodes
        self.client_id = client_id
        print(self.addr, self.nodes)
        self.tcp_bus = TcpBus(self.addr, self.nodes)

    def form_heartbeat_ack_msg(self):
        msg = can.Message(arbitration_id=canspecs.CAN_ID_HEARTBEAT_ACK,
                          data=struct.pack(canspecs.CAN_FORMAT_HEARTBEAT_ACK, self.client_id),
                          dlc=4)
        return msg

    def send_heartbeat_ack_msg(self, node_id: int):
        self.tcp_bus.send(self.form_heartbeat_ack_msg())

    def recv(self, timeout=1.0):
        return self.tcp_bus.recv(timeout)

    def main_loop(self):
        while True:
            r = self.tcp_bus.recv(1.0)
            #for node, nid in self.id_map.items():
            #    self.send_heartbeat_ack_msg(nid)
            #print(r)


if __name__ == "__main__":
    sm = ServiceMonitor("docker.service", "192.168.0.161")
    print(sm.is_healthy)
    om = OtaMonitor("https://www.google.com")
    print(om.is_healthy)

    tcp_descr = {"127.0.0.1:5555": 0x0,
                 "127.0.0.1:5556": cids.HACKER_KIOSK,
                 "127.0.0.1:5557": cids.INFOTAINMENT_SERVER_1,
                 "127.0.0.1:5558": cids.INFOTAINMENT_SERVER_2,
                 "127.0.0.1:5559": cids.INFOTAINMENT_SERVER_3}
    thm = TcpHeartbeatMonitor("127.0.0.1:5555", tcp_descr)
    clients = [TcpHeartbeatClient(addr, nid, tcp_descr) for addr, nid in tcp_descr.items()[::-1] if nid != 0]
    thm.send_req_nodes()
    # FIXME: order matters...
    for c in clients[::-1]:
        r = c.recv()
        print(r)