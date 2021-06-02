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
    while True:
        # Dummy
        socket.send_json(args.port)
        message = socket.recv()
        print(f"Status is: {message}")
        time.sleep(1.0)        
        
