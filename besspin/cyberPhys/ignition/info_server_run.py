"""
Project: SSITH CyberPhysical Demonstrator
Name: info_server_run.py
Author: Ethan Lew <elew@galois.com>
Date: 02/01/2021

Test Setup for Infotainment Mux Development

NOTE: not a pytest script as a modified infotainment server is needed to be launched
before running this script (see below)

Usage:
    Build the infotainment server with different SEND and RECEIVE ports, if
    testing on a single computer (set SEND to 5003, and RECEIVE to 5002)

    python info_server_run.py
"""
import struct, time
from cyberphys import can, canspecs, infotainment


class DumpListener(can.CanListener):
    """dump listener is to see what comes out of the infotainment server (IS)"""
    def recv(self, id: int, data_len: int, data: bytes):
        name =  None
        for n, v in canspecs.__dict__.items():
            if id == v:
                name = n
                break
        print(f"{self.name} id: {id} ({name}) len: {data_len} data: {data}")


# setup the in/out can networks
# NOTE: ports are hard-coded
can_net_out = can.CanUdpNetwork("can_out", 5002, "", do_bind=False)
can_net_in = can.CanUdpNetwork("can_in", 5003, "", do_bind=True)

# configure the networks
can_net_in.register(DumpListener("dump-listener-in"))
can_net_in.register(infotainment.InfotainmentUi(can_net_out))
can_net_in.start()

can_net_out.register(DumpListener("dump-listener-out"))
can_net_out.start()

# simulate can_out.py
pos = (0.0, 0.0, 0.0)
can_net_out.send(canspecs.CAN_ID_CAR_X, struct.pack("f", pos[0]))
can_net_out.send(canspecs.CAN_ID_CAR_Y, struct.pack("f", pos[0]))
can_net_out.send(canspecs.CAN_ID_CAR_Z, struct.pack("f", pos[0]))

# simulate UI -- change stations
can_net_out.send(canspecs.CAN_ID_BUTTON_PRESSED, struct.pack("B", 0x01))
time.sleep(1)
can_net_out.send(canspecs.CAN_ID_BUTTON_PRESSED, struct.pack("B", 0x02))
time.sleep(1)
can_net_out.send(canspecs.CAN_ID_BUTTON_PRESSED, struct.pack("B", 0x03))
time.sleep(1)

# turn music volume down
for _ in range(20):
    can_net_out.send(canspecs.CAN_ID_BUTTON_PRESSED, struct.pack("B", 0x10))
    time.sleep(0.1)

# turn music volume up
for _ in range(20):
    can_net_out.send(canspecs.CAN_ID_BUTTON_PRESSED, struct.pack("B", 0x11))
    time.sleep(0.1)

# terminate the threads
can_net_out.exit()
can_net_in.exit()
