
import struct
import socket
import select
import time
import zmq
from can import BusABC, Message

class CanConstants():
    CAN_MIN_BYTES = 4 + 1 + 1  # sending an empty frame doesn't make sense, min 6 bytes per frame
    CAN_MAX_BYTES = 64 + 4 + 1  # 64 bytes of DATA, 4 bytes of ID, 1 byte od DLC
    COMMAND_ID_PREFIX =  [0xAA, 0xFE, 0xEB] # CAN ID signifying a command message

class CommandBus(BusABC):
    """
    Command and Control bus over ZMQ TCP connection

    For guaranteed 'fake multicast' Publish/Subscribe communication
    """

    def __init__(self, host_ip_addr, subscriber_ip_addrs):
        super(CommandBus, self).__init__(channel="dummy")
        self.context = zmq.Context()
        self.publisher_addr = "tcp://" + host_ip_addr

        self.publisher = self.context.socket(zmq.PUB)
        # drop messages immediately if nobody is listening
        self.publisher.setsockopt(zmq.LINGER,0)
        try:
            print(f"<CommandBus> Binding to {self.publisher_addr}")
            self.publisher.bind(self.publisher_addr)
        except Exception as e:
            print(f"<CommandBus> Binding failed: {e}")

        self.subscribers = []
        for subscriber_ip_addr in subscriber_ip_addrs:
            addr = "tcp://" + subscriber_ip_addr
            if addr != self.publisher_addr:
                print(f"<CommandBus> Connecting publisher to {addr}")
                socket = self.context.socket(zmq.SUB)
                try:
                    socket.connect(addr)
                except Exception as e:
                    print(f"<CommandBus> Connecting failed: {e}")
                socket.setsockopt(zmq.SUBSCRIBE, bytes(CanConstants.COMMAND_ID_PREFIX))
                self.subscribers.append(socket)
                print(f"<CommandBus> Connection successfull!")

    def send(self, msg, timeout=None):
        a_id = struct.pack('!I', msg.arbitration_id)
        byte_msg = bytearray(a_id)
        byte_msg.append(msg.dlc)
        byte_msg += bytearray([msg.data[i] for i in range(0, msg.dlc)])
        if timeout:
            print("CommandBus Warning: timeout is ignored during send()")
        self.publisher.send(byte_msg)

    def _recv_internal(self, timeout):
        # Initialize poll set
        poller = zmq.Poller()
        for subscriber in self.subscribers:
            poller.register(subscriber, zmq.POLLIN)

        events = dict(poller.poll(timeout))
        for subscriber in self.subscribers:
            if subscriber in events and events[subscriber] == zmq.POLLIN:
                rx_data = subscriber.recv_multipart(flags=zmq.NOBLOCK)[0]
                print(f"rx_data = {rx_data}, type={type(rx_data)}, len={len(rx_data)}")
                if len(rx_data) < CanConstants.CAN_MIN_BYTES:
                    print("CommandBus Warning: received only {} bytes, ignoring.".format(len(rx_data)))
                elif len(rx_data) > CanConstants.CAN_MAX_BYTES:
                    print("UDPBus Warning: received {} bytes which is more than'\
                    'CAN_MAX_BYTES({CanConstants.CAN_MAX_BYTES}), ignoring.".format(len(rx_data)))
                else:
                    s = bytearray(rx_data[0:4])
                    arb_id = struct.unpack('!I', s)[0]
                    dlc = rx_data[4]
                    data = rx_data[5:]
                    if dlc == len(data):
                        msg = Message(timestamp=time.time(),
                                    arbitration_id=arb_id,
                                    dlc=dlc,
                                    data=data)
                        return msg, False
                    else:
                        print("UDPBus Warning: DLC ({}) and the length of data ({}) don't match, ignoring.".format(dlc,len(rx_data)))
        return None, False

class UDPBus(BusABC):
    """
    Enable basic communication over UDP

    The bus is bound to a particular ADDR and PORT upon creation,
    and can receive data only from that addr/port.

    The bus can send data to any address/port.
    """

    def __init__(self, bind_ip, bind_port):
        super(UDPBus, self).__init__(channel="dummy")
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.bind((bind_ip, bind_port))

    def send(self, msg, tx_ip, tx_port, timeout=None):
        a_id = struct.pack('!I', msg.arbitration_id)
        byte_msg = bytearray(a_id)
        byte_msg.append(msg.dlc)
        byte_msg += bytearray([msg.data[i] for i in range(0, msg.dlc)])
        if timeout:
            print("UDPBus Warning: timeout is ignored during send()")
        self._sock.sendto(byte_msg, (tx_ip, tx_port))

    def _recv_internal(self, timeout):
        ready = select.select([self._sock], [], [], timeout)
        if ready[0]:
            rx_data, _ = self._sock.recvfrom(CanConstants.CAN_MAX_BYTES)
            if len(rx_data) < CanConstants.CAN_MIN_BYTES:
                print("UDPBus Warning: received only {} bytes, ignoring.".format(len(rx_data)))
            else:
                s = bytearray(rx_data[0:4])
                arb_id = struct.unpack('!I', s)[0]
                dlc = rx_data[4]
                data = rx_data[5:]
                if dlc == len(data):
                    msg = Message(timestamp=time.time(),
                                arbitration_id=arb_id,
                                dlc=dlc,
                                data=data)
                    return msg, False
                else:
                    print("UDPBus Warning: DLC ({}) and the length of data ({}) don't match, ignoring.".format(dlc,len(rx_data)))
        return None, False
