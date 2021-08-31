#!/usr/env/python3
"""
Project: SSITH CyberPhysical Demonstrator
Name: monitor_health.py
Author:  Ethan Lew <elew@galois.com>
Date: 31 August 2021

Utility to Monitor SSITH CyberPhysical Demonstrator Component Health
"""
import cyberphyslib.demonstrator.health as cyhealth
import cyberphyslib.demonstrator.can as cycan
from cyberphyslib.demonstrator import config

import pathlib, os, time
import argparse
import pprint


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BESSPIN Demonstrator Ignition")
    parser.add_argument("-network-config", type=str, default="", help="Path to BESSPIN Target setupEnv.json")
    args = parser.parse_args()
    if args.network_config == "":
        network_filepath = pathlib.Path(
            os.path.realpath(__file__)).parent / ".." / ".." / "base" / "utils" / "setupEnv.json"
    else:
        network_filepath = args.network_config
    assert os.path.exists(network_filepath), f"specified network config json ({network_filepath}) doesn't exist"
    dnc = config.DemonstratorNetworkConfig.from_setup_env(network_filepath)

    # create buses for both the can (udp) and cc (tcp) buses
    print("Starting the CAN bus")
    udp_net = cycan.CanUdpNetwork("udp-net", dnc.port_network_canbusPort, dnc.ip_SimPc)
    udp_net.start()
    print("Starting the Tcp Bus")
    tcp_net = cycan.CanTcpNetwork("tcp-net", '10.88.88.4:5041', ['10.88.88.1:5041', '10.88.88.2:5041', '10.88.88.3:5041', '10.88.88.5:5041', '10.88.88.6:5041'] )
    tcp_net.start()

    # initialize and start the heartbeat component
    hm = cyhealth.HeartbeatMonitor(udp_net, tcp_net)
    hm.setup_can()
    hm.setup_cc()
    hm.start_monitor()
    hm.start()

    # run the main loop
    idx = 0
    start_time = time.time()
    while True:
        time.sleep(3.0)
        print(f"Health Status (Index {idx})(Uptime {time.time() - start_time: 2.3f} s)")
        pprint.pprint(hm.health_report)
        idx += 1