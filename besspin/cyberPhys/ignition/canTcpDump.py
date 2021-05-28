#!/usr/bin/env python3
'''
Project: SSITH CyberPhysical Demonstrator
Name: candump.py
Author: Steven Osborn <steven@lolsborn.com>
Date: 28 August 2020

Dumps all CAN traffic on CyberPhys network to stdout
'''
import argparse
import cyberphyslib.canlib as ccan


if __name__ == '__main__':
    # Setup the CAN Network
    print("Connecting Transmitter Thread...")
    cmdPort = 5041
    host = f"10.88.88.1:{cmdPort}"
    nodes = [f"10.88.88.2:{cmdPort}",f"10.88.88.3:{cmdPort}",f"10.88.88.3:{cmdPort}",f"10.88.88.4:{cmdPort}"]
    print(f"candump connecting to host {host} and nodes {nodes}")
    can_net = ccan.TcpBus(host, nodes)

    while True:
        msg = can_net.recv(timeout=1.0)
        if msg:
            print(msg)
