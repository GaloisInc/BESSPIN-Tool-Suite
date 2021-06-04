#!/usr/bin/env python3

import zmq
import time
import json
import random

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:3333")

while True:
    message = socket.recv()
    decoded = json.loads(message)
    print("Received request: %s" % decoded)

    # Check to see if this is a message we know about
    if decoded['event'] == "hack-info":
        
        # Do Something blocking
        time.sleep(1)

        # Send a status / state update to the client
        socket.send_string(json.dumps({'function': 'hack-info', 'status': 200}))

    elif decoded['event']['function'] == "changeStation":
        station = decoded['event']['args'][0]
        socket.send_string(json.dumps({'function': 'changeStation', 'retval': station, 'status': 200}))
    elif decoded['event']['function'] == "volumeUp":
        socket.send_string(json.dumps({'function': 'volumeUp','status': 200}))
    elif decoded['event']['function'] == "volumeDown":
        socket.send_string(json.dumps({'function': 'volumeDown', 'status': 200}))
    elif decoded['event']['function'] == "exfil":
        x = round(random.uniform(0.33, 266.66), 2)
        y = round(random.uniform(33.33, 380.66), 2)
        z = round(random.uniform(0.33, 360.66), 2)
        socket.send_string(json.dumps({'function': 'exfil', 'status': 200, 'retval': [x, y, z]}))


    time.sleep(.5)

