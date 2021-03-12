#!/usr/bin/env python
"""
Project: SSITH CyberPhysical Demonstrator
Name: outgaugedump.py
Author: Steven Osborn <steven@lolsborn.com>
Date: 27 August 2020

Simple utility for debugging outguage data streams.  Will listen for packets
and print them to stdout
"""
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 4444
BUFFER_SIZE = 1000


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    data = sock.recv(BUFFER_SIZE)
    print(data)
