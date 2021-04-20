#!/usr/bin/env python
'''
Project: SSITH CyberPhysical Demonstrator
Name: cansend.py
Author: Steven Osborn <steven@lolsborn.com>
Date: 28 August 2020

Utility to send a CAN packet over UDP to the cyberphys vehicle network
'''
import socket

from demonstrator import can, config
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send CAN packet over UDP")
    parser.add_argument("id", type=int, help="CAN id")
    parser.add_argument("data", type=str, help="Message")
    parser.add_argument("-port", type=int, default=config.CAN_PORT, help="Network port")

    args = parser.parse_args()

    net = can.CanUdpNetwork("cansend", args.port, "")
    net.send(args.id, args.data)
