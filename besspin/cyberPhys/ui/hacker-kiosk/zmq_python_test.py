#!/usr/bin/env python3

import zmq
import time
import json

context = zmq.Context()
socket = context.socket(zmq.PAIR)
socket.bind("tcp://*:3333")

while True:
    message = socket.recv()
    decoded = json.loads(message)
    print("Received request: %s" % decoded)

    # Check to see if this is a message we know about
    if decoded['type'] == "cmd-msg" and decoded['event'] == "hack-info":
        
        # Do Something blocking
        time.sleep(1)

        # Send a status / state update to the client
        socket.send_string(json.dumps({'type': 'state-change', 'state': 'hack-info-success'}))

    time.sleep(.5)

