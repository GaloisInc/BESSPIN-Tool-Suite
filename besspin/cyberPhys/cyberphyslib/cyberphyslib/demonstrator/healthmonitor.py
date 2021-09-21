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
            #health_logger.debug(f"Exception {exc} has occurred")
            return False


class OtaMonitor(HttpMonitor):
    """
    Monitor Infotainment Ota Process (via HTTP request)
    """
    def check_response(self, ret: requests.Response) -> bool:
        return ret.status_code == 200

class HeartbeatMonitor(threading.Thread):
    FREQUENCY = 0.1

    def __init__(self):
        threading.Thread.__init__(self,daemon=True)
        self.https = {
                cids.OTA_UPDATE_SERVER_1 : "http://10.88.88.11:5050",
                cids.OTA_UPDATE_SERVER_2 : "http://10.88.88.21:5050",
                cids.OTA_UPDATE_SERVER_3 : "http://10.88.88.31:5050"
            }
    
        self.ota_monitors = {k: OtaMonitor(addr) for k, addr in self.https.items()}
        self._health_report = {}
    
    def run(self):
        while True:
            ret = {}
            health_logger.debug("Testing OTA")
            for k, v in self.ota_monitors.items():
                hs = v.is_healthy
                ret[k] = hs
                if not hs:
                    health_logger.debug(f"WARNING! {k} HTTP failed health check")
            
            self._health_report = ret

            time.sleep(1.0/self.FREQUENCY)
    
    @property
    def health_report(self):
        return self._health_report