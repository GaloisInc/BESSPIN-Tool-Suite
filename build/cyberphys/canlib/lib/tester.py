#!/usr/bin/python3
import struct
import socket
import select
import time
from can import BusABC, Message

BIND_PORT = 5002
TX_PORT = 5001
TX_IP = "10.88.88.2"

class UDPBus(BusABC):
    """
    Enable basic communication over UDP

    The bus is bound to a particular ADDR and PORT upon creation,
    and can receive data only from that addr/port.

    The bus can send data to any address/port.
    """
    CAN_MIN_BYTES = 4 + 1 + 1  # sending an empty frame doesn't make sense, min 6 bytes per frame
    CAN_MAX_BYTES = 64 + 4 + 1  # 64 bytes of DATA, 4 bytes of ID, 1 byte od DLC

    def __init__(self, bind_port):
        self.port = bind_port
        super(UDPBus, self).__init__(channel="dummy")
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.bind(("", self.port))

    def send(self, msg, tx_ip, tx_port, timeout=None):
        a_id = struct.pack('<I', msg.arbitration_id)
        byte_msg = bytearray(a_id)
        byte_msg.append(msg.dlc)
        byte_msg += bytearray([msg.data[i] for i in range(0, msg.dlc)])
        if timeout:
            print("Warning: ignoring timeout {}".format(timeout))
        self._sock.sendto(byte_msg, (tx_ip, tx_port))

    def _recv_internal(self, timeout):
        ready = select.select([self._sock], [], [], timeout)
        if ready[0]:
            rx_data, sender_addr = self._sock.recvfrom(UDPBus.CAN_MAX_BYTES)
            print("Info: received {} bytes from {}".format(len(rx_data), sender_addr))
            if len(rx_data) < UDPBus.CAN_MIN_BYTES:
                print("Warning: received only {} bytes, ignoring.".format(len(rx_data)))
            else:
                s = bytearray(rx_data[0:4])
                arb_id = struct.unpack('<I', s)[0]
                dlc = rx_data[4]
                if dlc == len(rx_data[5:]):
                    data = rx_data[5:]
                    msg = Message(timestamp=time.time(),
                                arbitration_id=arb_id,
                                dlc=dlc,
                                data=data)
                    return msg, False
                else:
                    print("Warning: DLC ({}) and the length of data ({}) don't match, ignoring.".format(dlc,len(rx_data)))
        return None, False


bus = UDPBus(BIND_PORT)

# send a message
message = Message(arbitration_id=0XAAFEEE00, is_extended_id=True,
                  data=[0xAA, 0xBB, 0xCC, 0xDD])

# iterate over received messages
for msg in bus:
    print(f"id={hex(msg.arbitration_id)}, data={msg.data}")
    bus.send(message, TX_IP,TX_PORT)

