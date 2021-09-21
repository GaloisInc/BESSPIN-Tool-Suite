"""
Project: SSITH CyberPhysical Demonstrator
health.py
Author: Ethan Lew <elew@galois.com>
Date: 08/23/2021
Python 3.8.3
O/S: Windows 10

Component Health Monitoring Objects and Components
"""
import threading
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
import subprocess


from cyberphyslib.canlib import TcpBus, UdpBus
import cyberphyslib.canlib.canspecs as canspecs
import cyberphyslib.canlib.componentids as cids
import cyberphyslib.demonstrator.component as cycomp
import cyberphyslib.demonstrator.can as cycan
from cyberphyslib.demonstrator.logger import health_logger



def ip2int(ip):
    """Convert an IP string to an int"""
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]

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

class PingMonitor(HealthMonitor):
    """
    If this monitor receives can succesfully ping the component,
    it considers it healthy
    """
    def __init__(self, addr: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addr = addr

    def run_health_test(self) -> bool:
        retCode = subprocess.call(["ping","-w","1",self.addr])
        if retCode == 0:
            return True
        else:
            return False

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
            health_logger.debug(f"<{self.__class__.__name__}> Exception {exc} has occurred")
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
            return re.search(r"(Active: active \(running\))", ret.stdout) is not None
        except Exception as exc:
            health_logger.debug(f"<{self.__class__.__name__}> Exception {exc} has occurred")
            return False


class OtaMonitor(HttpMonitor):
    """
    Monitor Infotainment Ota Process (via HTTP request)
    """
    def check_response(self, ret: requests.Response) -> bool:
        return ret.status_code == 200





HeartbeatResponseType = typing.Tuple[float, float]

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
        self.response_buffer: typing.Dict[int, typing.Deque[float]] = {
            c: collections.deque(maxlen=self.maxlen) for c in client_ids
        }
        self.start_time = time.time()

    def submit_response(self, client_id: int, response: HeartbeatResponseType):
        """submit a response from client_id to the ACK buffer"""
        if client_id not in self.response_buffer:
            # TODO: FIXME: add fault location
            idmap = {v: k for k, v in cids.__dict__.items() if isinstance(v, int)}
            cname = idmap.get(client_id, "<UNKNOWN>")
            health_logger.warning(f"<{self.__class__.__name__}> Received unanticipated response {client_id} ({cname})")
        else:
            if response is not None:
                self.response_buffer[client_id].append(time.time())

    def send_heartbeat_req_msg(self, req_number: int):
        """set REQ can packet over the TCP bus"""
        m = self.form_heartbeat_req_msg(req_number)
        self.bus.send_msg(m)

    def send_req_nodes(self):
        """send REQ to nodes"""
        self.send_heartbeat_req_msg(self.curr_req_number)
        self.curr_req_number += 1

    def run_health_test(self) -> bool:
        """implement the heartbeat health:
            for a given history of component with component id cid, if the maximum value is
            within MAXLEN of the current REQ number, the component is considered healthy
        """
        return all(self.run_health_tests())

    def run_health_tests(self) -> typing.Dict[typing.Hashable, bool]:
        """return health result for each component entered in the response buffer"""
        outcome = {k: True for k in self.response_buffer.keys()}
        for cid, buff in self.response_buffer.items():
            if len(buff) > 0:
                ltime = max(buff)
                delta = time.time() - ltime
                if delta > self.maxlen:
                    health_logger.debug(f"ERROR: Component with ID {cid} Has Failed Heartbeat Health Test!")
                    outcome[cid] = False
            else:
                if time.time() - self.start_time > self.wait_period:
                    health_logger.debug(f"ERROR: Component with ID {cid} Has Failed Heartbeat Health Test (No Submissions)!")
                    outcome[cid] = False
        return outcome

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
    def __init__(self, *args, heartbeat_sample_period=1.0, **kwargs):
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
        self._heartbeat_monitor_udp: typing.Optional[BusHeartbeatMonitor] = None

    def register_can_heartbeat_bus(self, bus: UdpBus, client_ids):
        self._heartbeat_monitor_udp: BusHeartbeatMonitor = BusHeartbeatMonitor(client_ids, bus)

    def on_heartbeat_poll(self, t):
        if self._heartbeat_monitor_udp is not None:
            hm: BusHeartbeatMonitor = self._heartbeat_monitor_udp
            hm.send_req_nodes()

    def run_health_test(self) -> bool:
        udp_result = True
        if self._heartbeat_monitor_udp is not None:
            hm: BusHeartbeatMonitor = self._heartbeat_monitor_udp
            udp_result = hm.run_health_test()
        return udp_result

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
        cid, rnum = data
        if self._heartbeat_monitor_udp is not None:
            self._heartbeat_monitor_udp.submit_response(cid, (cid, rnum))
















class HeartbeatMonitor(threading.Thread):
    FREQUENCY = 0.1

    def __init__(self):
        threading.Thread.__init__(self,daemon=True)
        self.services = {
            cids.CAN_DISPLAY_FRONTEND:
                {
                    "user" : "pi",
                    "password": "WelcomeToGalois",
                    "address" : "10.88.88.5",
                    "service_name": "can-ui"
                },
            cids.HACKER_KIOSK_FRONTEND:
                {
                    "user" : "pi",
                    "password": "WelcomeToGalois",
                    "address" : "10.88.88.3",
                    "service_name": "hacker-ui"
                },
            cids.INFOTAINMENT_THIN_CLIENT:
                {
                    "user" : "pi",
                    "password": "WelcomeToGalois",
                    "address" : "10.88.88.2",
                    "service_name": "infotainment"
                }
                    }
        self.https = {
                cids.OTA_UPDATE_SERVER_1 : "http://10.88.88.11:5050",
                cids.OTA_UPDATE_SERVER_2 : "http://10.88.88.21:5050",
                cids.OTA_UPDATE_SERVER_3 : "http://10.88.88.31:5050"
            }
        self.pings = {
            cids.DEBIAN_1 : "10.88.88.11",
            cids.DEBIAN_2_LMCO : "10.88.88.21",
            cids.DEBIAN_3 : "10.88.88.31",
        }

        self.component_monitor = HeartbeatMonitorComponent("can_monitor", set(), set())
        self.ping_monitors  = {k: PingMonitor(addr) for k, addr in self.pings.items()}
        self.ota_monitors = {k: OtaMonitor(addr) for k, addr in self.https.items()}
        self.service_monitors = {k: ServiceMonitor(params["service_name"], params["address"],
                                                   user=params["user"],
                                                   password=params["password"]) for k, params in self.services.items()}
        self._health_report = {}
    
    def start_monitor(self, can_bus):
        """monitor initialization"""
        can_bus.register(self.component_monitor)
        self.component_monitor.register_can_heartbeat_bus(can_bus.bus, self.udp_descr.values())
        self.component_monitor.start()

    def run(self):
        while True:
            ret = {}
            health_logger.debug("Testing OTA")
            for k, v in self.ota_monitors.items():
                hs = v.is_healthy
                ret[k] = hs
                if not hs:
                    health_logger.debug(f"WARNING! {k} HTTP failed health check")
            
            health_logger.debug("Testing Services")
            for k, v in self.service_monitors.items():
                hs = v.is_healthy
                ret[k] = hs
                if not hs:
                    health_logger.debug(f"WARNING! {k} Service failed health check")

            health_logger.debug("Testing Ping")
            for k, v in self.ping_monitors.items():
                hs = v.is_healthy
                ret[k] = hs
                if not hs:
                    health_logger.debug(f"WARNING! {k} Ping failed health check")
            
            if self.component_monitor is not None:
                # TODO: this monitor access is ugly
                if self.component_monitor._heartbeat_monitor_udp is not None:
                    health_logger.debug("Testing UDP")
                    health_report = self.component_monitor._heartbeat_monitor_udp.run_health_tests()
                    kmap = {v: k for k,v in self.udp_descr.items()}
                    ret.update({kmap[k]: v for k, v in health_report.items()})
                    if not all(health_report.values()):
                        health_logger.debug(f"Health Status: {health_report}")
                        health_logger.debug(f"ERROR! UDP Failed")

            self._health_report = ret

            time.sleep(1.0/self.FREQUENCY)
    
    @property
    def health_report(self):
        return self._health_report