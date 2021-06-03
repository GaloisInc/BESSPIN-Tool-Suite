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
    if decoded['event'] == "hack-info":
        
        # Do Something blocking
        time.sleep(1)

        # Send a status / state update to the client
        socket.send_string(json.dumps({'function': 'hack-info', 'retval': 200}))

    elif decoded['event']['function'] == "changeStation":
        socket.send_string(json.dumps({'function': 'changeStation', 'args': [3], 'retval': 200}))


    time.sleep(.5)

