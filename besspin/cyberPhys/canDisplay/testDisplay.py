#!/usr/bin/env python3
"""
Simple CAN listener. Listens to CAN CMD messages,
update the display when status changes.

Exchange format:
{
    func: "name-of-the-function-to-be-called",
    args: {"dictionary of arguments}
    resp: {"dictionary of return vaues}
    status: response status
        200 -OK
        500 - unexpected failure
        501 - func not implemented
}
"""

import time
import logging
import zmq
import argparse

from cyberphyslib.demonstrator import can

# make CAN module less noisy
logging.getLogger("can").setLevel(logging.WARNING)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Frontend test for CAN display")
    parser.add_argument("-port", type=int, help="ZMQ port")
    args = parser.parse_args()

    if not args.port:
        args.port = 5091

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    addr = f"tcp://localhost:{args.port}"
    print(f"Connecting to {addr}")
    socket.connect(addr)
    req = {}
    req['func'] = "serveScenarioStatus"
    req['args'] = {}

    while True:
        # Dummy
        socket.send_json(req)
        recv = socket.recv_json()
        print(f"{recv}")
        assert("func" in recv and "args" in recv and 'retval' in recv and 'status' in recv)
        scenarioStatus = recv['retval']
        print(f"scenarioStatus={scenarioStatus}")
        time.sleep(1.0)        
        
