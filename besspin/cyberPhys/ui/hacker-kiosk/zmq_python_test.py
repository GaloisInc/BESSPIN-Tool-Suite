#!/usr/bin/env python3

import zmq
import time
import json
import random

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5091")

while True:
    message = socket.recv()
    decoded = json.loads(message)
    print("Received request: %s" % decoded)

    # Check to see if this is a message we know about
    if decoded['func'] == "Hack05_InfoAttempt":
        
        # Do Something blocking
        time.sleep(1)

        # Send a status / state update to the client
        socket.send_string(json.dumps({'func': 'Hack05_InfoAttempt', 'status': 200}))

    elif decoded['func'] == "changeStation":
        station = decoded['func']['args'][0]
        socket.send_string(json.dumps({'func': 'changeStation', 'retval': station, 'status': 200}))
    elif decoded['func'] == "volumeUp":
        socket.send_string(json.dumps({'func': 'volumeUp','status': 200}))
    elif decoded['func'] == "volumeDown":
        socket.send_string(json.dumps({'func': 'volumeDown', 'status': 200}))
    elif decoded['func'] == "exfil":
        x = round(random.uniform(0.33, 266.66), 2)
        y = round(random.uniform(33.33, 380.66), 2)
        z = round(random.uniform(0.33, 360.66), 2)
        socket.send_string(json.dumps({'func': 'exfil', 'status': 200, 'retval': [x, y, z]}))


    time.sleep(.5)

