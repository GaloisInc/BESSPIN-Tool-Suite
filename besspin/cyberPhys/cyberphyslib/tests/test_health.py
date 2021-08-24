"""
Project: SSITH CyberPhysical Demonstrator
Name: test_health.py
Author: Ethan Lew
Date: 23 August 2021

Test for Component Health Monitoring
"""
from cyberphyslib.demonstrator.health import *
import cyberphyslib.canlib.componentids as cids

import time


def test_service_health():
    """test the component object

    operational tests:
    failure mode tests:
    """
    pass
    # TODO: how to test
    #sm = ServiceMonitor("docker.service", "<ADDR>")
    #assert sm.is_healthy


def test_ota_health():
    """test HTTP Ota monitoring

    operational tests:
        1. monitor connection to website
    failure mode tests:
        1. monitor connection to website that doesn't exist
    """
    om = OtaMonitor("https://www.google.com")
    assert om.is_healthy

    om = OtaMonitor("https://www.djsldjaldjewopwei.com")
    assert not om.is_healthy


def test_tcp_heartbeat():
    """test the 1-N TCP Heartbeat Monitoring

    operational tests:
        1. all clients operating correctly
    failure mode tests:
        1. client fails to provide heartbeat soon enough
    """
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

    clients = [HeartbeatClientComponent(f"client-{idx}", set(), set()) \
               for idx in range(len(tcp_descr) - 1)]

    thm.start()
    thm.start_poller()
    for c, (addr, cid) in zip(clients, ((a, c) for a, c in tcp_descr.items() if c != 0)):
        c.register_heartbeat_bus(TcpBus(addr, ["127.0.0.1:5555"]), cid)
        c.start()
        c.start_poller()

    time.sleep(10.0)
    assert thm.is_healthy
    clients[-1].exit()
    time.sleep(10.0)
    assert not thm.is_healthy

    for c in clients:
        c.exit()
    thm.exit()