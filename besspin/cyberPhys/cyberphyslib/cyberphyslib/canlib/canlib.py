
import struct
import socket
import select
import time
import zmq
import typing as typ
from can import BusABC, Message

# custom types for can bus
CanDataType = typ.Union[bytes, str]
NetworkListType = typ.Union[typ.Sequence[str], None, bool]

# custom error(s)
class InvalidCanMessageError(Exception):
    pass

class CanConstants():
    DEST_BROADCAST = "<broadcast>"
    CAN_MIN_BYTES = 4 + 1 + 1  # sending an empty frame doesn't make sense, min 6 bytes per frame
    CAN_MAX_BYTES = 64 + 4 + 1  # 64 bytes of DATA, 4 bytes of ID, 1 byte od DLC
    COMMAND_ID_PREFIX =  [0xAA] # CAN ID signifying a command message

class TcpBus(BusABC):
    """
    CAN bus with guaranteed delivery using ZMQ over TCP

    For guaranteed 'fake multicast' Publish/Subscribe communication
    """

    def __init__(self, host_ip_addr: str, subscriber_ip_addrs: typ.Sequence[str]):
        super(TcpBus, self).__init__(channel="dummy")
        self.context = zmq.Context()
        self.publisher_addr = "tcp://" + host_ip_addr

        self.publisher = self.context.socket(zmq.PUB)
        # drop messages immediately if nobody is listening
        self.publisher.setsockopt(zmq.LINGER,0)
        print(f"<{self.__class__.__name__}> Binding to {self.publisher_addr}")
        self.publisher.bind(self.publisher_addr)

        self.subscribers = []
        for subscriber_ip_addr in subscriber_ip_addrs:
            addr = "tcp://" + subscriber_ip_addr
            if addr != self.publisher_addr:
                print(f"<{self.__class__.__name__}> Connecting publisher to {addr}")
                socket = self.context.socket(zmq.SUB)
                try:
                    socket.connect(addr)
                except Exception as e:
                    print(f"<{self.__class__.__name__}> Connecting failed: {e}")
                socket.setsockopt(zmq.SUBSCRIBE, bytes(CanConstants.COMMAND_ID_PREFIX))
                self.subscribers.append(socket)
                print(f"<{self.__class__.__name__}> Connection successfull!")

    def send(self, msg, timeout=None):
        a_id = struct.pack('!I', msg.arbitration_id)
        byte_msg = bytearray(a_id)
        byte_msg.append(msg.dlc)
        byte_msg += bytearray([msg.data[i] for i in range(0, msg.dlc)])
        if timeout:
            print(f"<{self.__class__.__name__}> Warning: ignoring timeout of {timeout} [s] during send()")
        self.publisher.send(byte_msg)

    def send_msg(self, msg):
        self.send(msg)

    def _recv_internal(self, timeout):
        # Initialize poll set
        poller = zmq.Poller()
        for subscriber in self.subscribers:
            poller.register(subscriber, zmq.POLLIN)

        events = dict(poller.poll(timeout))
        for subscriber in self.subscribers:
            if subscriber in events and events[subscriber] == zmq.POLLIN:
                rx_data = subscriber.recv_multipart(flags=zmq.NOBLOCK)[0]
                if len(rx_data) < CanConstants.CAN_MIN_BYTES:
                    print(f"<{self.__class__.__name__}> Warning: received only {len(rx_data)} bytes, ignoring.")
                elif len(rx_data) > CanConstants.CAN_MAX_BYTES:
                    print(f"<{self.__class__.__name__}> Warning: received {len(rx_data)} bytes which is more than'\
                    'CAN_MAX_BYTES({CanConstants.CAN_MAX_BYTES}), ignoring.")
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
                        print(f"<{self.__class__.__name__}> Warning: DLC ({dlc}) and the length of data\
                             ({len(rx_data)}) don't match, ignoring.")
        return None, False

class UdpBus(BusABC):
    """
    Enable basic communication over UDP

    The bus is bound to a particular ADDR and PORT upon creation,
    and can receive data only from that addr/port.

    The bus can send data to any address/port.
    """
    @staticmethod
    def check_network_list(net_list: NetworkListType) -> NetworkListType:
        """determine if a list of ips is a valid blacklist/whitelist. If valid, return it.
        Else, raise a value error
        :param net_list: list
        :return network list
        """
        try:
            if net_list:
                [socket.inet_aton(s) for s in net_list]
        except Exception:
            raise ValueError
        return net_list

    def __init__(self, port: int,
                 ip: str,
                 whitelist: NetworkListType = None,
                 blacklist: NetworkListType = None,
                 do_bind: bool = True):
        """
        :param port: port to send / receive can messages
        :param ip: ip to bind udp socket
        :param whitelist: None or list of ips to accept
        :param blacklist: None or list of ips to reject
        """
        self.ip = CanConstants.DEST_BROADCAST
        self.port = port
        self._whitelist = self.check_network_list(whitelist)
        self._blacklist = self.check_network_list(blacklist)
        super(UdpBus, self).__init__(channel="dummy")
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if do_bind:
            self._sock.bind((ip, self.port))

    def send(self, msg, timeout=None, tx_ip=None, tx_port=None):
        if not tx_port:
            tx_port=self.port
        if not tx_ip:
            tx_ip=self.ip
        try:
            if msg.dlc < 1:
                raise InvalidCanMessageError
            a_id = struct.pack('!I', msg.arbitration_id)
            byte_msg = bytearray(a_id)
            byte_msg.append(msg.dlc)
            byte_msg += bytearray([msg.data[i] for i in range(0, msg.dlc)])
        except Exception:
            raise InvalidCanMessageError(f"msg -- id {msg.arbitration_id}, dlc {msg.dlc}, data {msg.data}")
        if timeout:
            print(f"<{self.__class__.__name__}> Warning: ignoring timeout of {timeout} [s] during send()")
        self._sock.sendto(byte_msg, (tx_ip, tx_port))

    def send_msg(self, msg):
        self.send(msg)

    def _recv_internal(self, timeout):
        ready = select.select([self._sock], [], [], timeout)
        if ready[0]:
            rx_data, (sender_addr, _) = self._sock.recvfrom(CanConstants.CAN_MAX_BYTES)
            # ignore received data following whitelist, blacklist policy
            if self.whitelist:
                if sender_addr not in self.whitelist:
                    return None, False
            if self.blacklist:
                if sender_addr in self.blacklist:
                    return None, False
            if len(rx_data) < CanConstants.CAN_MIN_BYTES:
                print(f"<{self.__class__.__name__}> received only {len(rx_data)} bytes, ignoring.")
            else:
                s = bytearray(rx_data[0:4])
                arb_id = struct.unpack('!I', s)[0]
                dlc = rx_data[4]
                if dlc == len(rx_data[5:]):
                    data = rx_data[5:]
                    msg = Message(timestamp=time.time(),
                                  arbitration_id=arb_id,
                                  dlc=dlc,
                                  data=data)
                    return msg, False
                else:
                    print(f"<{self.__class__.__name__}> Warning: DLC ({dlc}) and the length of data\
                            ({len(rx_data)}) don't match, ignoring.")
        return None, False

    def shutdown(self):
        self._sock.close()

    @property
    def whitelist(self):
        return self._whitelist

    @whitelist.setter
    def whitelist(self, wl: NetworkListType):
        self._whitelist = self.check_network_list(wl)

    @property
    def blacklist(self):
        return self._blacklist

    @blacklist.setter
    def blacklist(self, bl: NetworkListType):
        self._blacklist = self.check_network_list(bl)
