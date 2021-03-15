#!/usr/bin/env python3
'''
Project: SSITH CyberPhysical Demonstrator
Name: candump.py
Author: Steven Osborn <steven@lolsborn.com>
Date: 28 August 2020

Dumps all CAN traffic on CyberPhys network to stdout
'''
import sys
import time
import socket
import argparse
from cyberphys import can, config

import logging
# make CAN module less noisy
logging.getLogger("can").setLevel(logging.WARNING)


BUFFER_SIZE = 1024


class DumpListener(can.CanListener):

    def recv(self, id: int, data_len: int, data: bytes):
        print(f"id: 0x{id:02X} len: {data_len} data: {data}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dump CAN over UDP traffic.")
    parser.add_argument("-port", type=int, default=config.CAN_PORT, help="Network port")
    args = parser.parse_args()

    print(f"candump listening on port {args.port}...")
    can_net = can.CanUdpNetwork("candump", args.port, "")
    listener = DumpListener("dump")
    can_net.register(listener)
    for msg in can_net.recv_iter():
        print(msg)
