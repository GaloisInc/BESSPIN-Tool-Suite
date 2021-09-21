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
        retCode = subprocess.call(["ping","-w","1",self.addr],
                                  stdout=subprocess.DEVNULL)
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




class HeartbeatMonitorComponent(cycomp.ComponentPoller):
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
    def __init__(self, bus: UdpBus):
        super().__init__("hbmonitor", [], [], sample_frequency=1.0)
        self.udp_bus = bus
        self.req_number = 0

    @staticmethod
    def form_heartbeat_req_msg(req_number: int):
        """form REQ can packet"""
        msg = can.Message(arbitration_id=canspecs.CAN_ID_HEARTBEAT_REQ,
                          data=struct.pack(canspecs.CAN_FORMAT_HEARTBEAT_REQ, req_number))
        return msg

    def on_poll_poll(self, t):
        # send heartbeat request
        self.req_number += 1
        m = self.form_heartbeat_req_msg(self.req_number)
        self.udp_bus.send_msg(m)

    @property
    def is_healthy(self) -> bool:
        """health property"""
        return False

    @property
    def is_unhealthy(self) -> bool:
        return not self.is_healthy

    @recv_can(canspecs.CAN_ID_HEARTBEAT_ACK, canspecs.CAN_FORMAT_HEARTBEAT_ACK)
    def _(self, data):
        """UDP Acknowledge: submit the ack to the monitor"""
        cid, rnum = data
        print(f"Got response from component {cid} rnum {rnum}")

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

        self.component_monitor = None
        self.ping_monitors  = {k: PingMonitor(addr) for k, addr in self.pings.items()}
        self.ota_monitors = {k: OtaMonitor(addr) for k, addr in self.https.items()}
        self.service_monitors = {k: ServiceMonitor(params["service_name"], params["address"],
                                                   user=params["user"],
                                                   password=params["password"]) for k, params in self.services.items()}
        self._health_report = {}
    
    def start_monitor(self, can_bus):
        """monitor initialization"""
        self.component_monitor = HeartbeatMonitorComponent(can_bus)
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

            self._health_report = ret

            time.sleep(1.0/self.FREQUENCY)
    
    @property
    def health_report(self):
        return self._health_report