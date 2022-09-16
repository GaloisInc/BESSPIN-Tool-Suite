"""
Project: SSITH CyberPhysical Demonstrator
Name: test_health.py
Author: Ethan Lew
Date: 23 August 2021

Test for Component Health Monitoring
"""
from cyberphyslib.demonstrator.health import *
import cyberphyslib.canlib.componentids as cids
import cyberphyslib.demonstrator.can as cycan

import time


def test_service_health():
    """test the service healthcheck

    operational tests:
    failure mode tests:
    """
    pass
    # TODO: how to test
    #sm = ServiceMonitor("docker.service", "<ADDR>")
    #assert sm.is_healthy


def test_udp_heartbeat():
    """test the UDP heartbeat component

    operational tests:
    failure mode tests:
    """
    net = cycan.CanUdpNetwork("name", 5030, "127.0.0.1")
    net.start()
    print("test UDP")

    cid_descr = {cids.HACKER_KIOSK, cids.INFOTAINMENT_SERVER_1, cids.INFOTAINMENT_SERVER_2, cids.INFOTAINMENT_SERVER_3}
    thm = HeartbeatMonitorComponent("monitor", set(), set())
    net.register(thm)
    thm.register_can_heartbeat_bus(net.bus, cid_descr)
    clients = [HeartbeatClientComponent(f"client-{idx}", set(), set()) \
               for idx in range(4)]
    thm.start()
    thm.start_poller()
    for c, cid in zip(clients, cid_descr):
        c.register_can_heartbeat_bus(net.bus, cid)
        net.register(c)
        #c.start()
        #c.start_poller()

    time.sleep(5.0)
    assert thm.is_healthy
    #clients[-1].exit()
    #clients[-1].join()
    #time.sleep(5.0)
    #assert not thm.is_healthy

    #for c in clients:
    #    c.exit()
    #    c.join()
    thm.exit()
    thm.join()
    net.exit()
    net.join()


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

    time.sleep(5.0)
    assert thm.is_healthy
    clients[-1].exit()
    time.sleep(5.0)
    assert not thm.is_healthy

    for c in clients:
        c.exit()
        c.join()
    thm.exit()
    thm.join()