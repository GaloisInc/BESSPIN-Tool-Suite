"""
Project: SSITH CyberPhysical Demonstrator
Name: can.py
Author: Steven Osborn <steven@lolsborn.com>, Ethan Lew <elew@galois.com>
Date: 26 August 2020

CAN Packet encoder / decoder
"""
import abc
import struct
import socket
import time
import select
import typing as typ
from abc import ABCMeta, abstractmethod
from can import BusABC, Message
from .logger import can_logger
from .component import ThreadExiting


# custom types for can bus
CanDataType = typ.Union[bytes, str]
NetworkListType = typ.Union[typ.Sequence[str], None, bool]


# custom error(s)
class InvalidCanMessageError(Exception):
    pass


class UDPBus(BusABC):
    """
    Enable basic communication over UDP

    The bus is bound to a particular ADDR and PORT upon creation,
    and can receive data only from that addr/port.

    The bus can send data to any address/port.
    """
    DEST_BROADCAST = "<broadcast>"
    CAN_MIN_BYTES = 4 + 1 + 1  # sending an empty frame doesn't make sense, min 6 bytes per frame
    CAN_MAX_BYTES = 64 + 4 + 1  # 64 bytes of DATA, 4 bytes of ID, 1 byte od DLC

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
        self.ip = self.DEST_BROADCAST
        self.port = port
        self._whitelist = self.check_network_list(whitelist)
        self._blacklist = self.check_network_list(blacklist)
        super(UDPBus, self).__init__(channel="dummy")
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        if do_bind:
            self._sock.bind((ip, self.port))

    def send(self, msg: Message, timeout=None):
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
            can_logger.warning("ignoring timeout {}".format(timeout))
        self._sock.sendto(byte_msg, (self.ip, self.port))

    def _recv_internal(self, timeout):
        ready = select.select([self._sock], [], [], timeout)
        if ready[0]:
            rx_data, (sender_addr, port) = self._sock.recvfrom(UDPBus.CAN_MAX_BYTES)
            # ignore received data following whitelist, blacklist policy
            if self.whitelist:
                if sender_addr not in self.whitelist:
                    return None, False
            if self.blacklist:
                if sender_addr in self.blacklist:
                    return None, False
            if len(rx_data) < UDPBus.CAN_MIN_BYTES:
                can_logger.warning("received only {} bytes, ignoring.".format(
                    len(rx_data)))
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
                    can_logger.warning(
                        "DLC ({}) and the length of data ({}) don't match, ignoring."
                        .format(dlc, len(rx_data)))
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


class CanListener(metaclass=ABCMeta):
    """
    Abstract CAN network listener.

    Listeners can be registered with an individual network or with
    the CAN multiverse.  A listener is registered using it's instance
    which is identified by it's name property and unregistered
    using that name.
    """
    def __init__(self, name):
        self.name = name

    """
    :param id: unsigned 32
    :param len: unsigned 8
    :param data: byte[]
    """
    @abstractmethod
    def recv(self, can_id: int, data_len: int, bytes_in):
        pass


class ExampleListener(CanListener):
    """
    Example implementation of a CAN network listner that just
    prints incoming packets to the console.
    """
    def __init__(self):
        super().__init__("example-listener")

    def recv(self, can_id: int, data_len: int, data: bytes):
        print(f">>> [ExampleListener] received packet {can_id} {data_len} {data}")


class CanNetwork(ThreadExiting, abc.ABC):
    """
    Abstract Interface for CAN Network Components

    CAN Networks define a way to send a packet and allows registration of
    CanListener objects.
    """
    POLL_RECV_TIMEOUT = 0.2

    def __init__(self, name: str):
        super(CanNetwork, self).__init__(name)
        self.name = name
        self._listeners = {}

    @abc.abstractmethod
    def send(self, can_id: int, data: CanDataType) -> None:
        """send a single can message"""
        raise NotImplementedError

    @abc.abstractmethod
    def recv(self, timeout=None) -> typ.Union[None, typ.Tuple[int, Message]]:
        """yield an iterator of incoming messages"""
        raise NotImplementedError

    def recv_iter(self) -> typ.Iterator[typ.Tuple[int, Message]]:
        """create an iterator of received can messages"""
        while True:
            yield self.recv()

    def register(self, listener: CanListener) -> None:
        """register a listener to the CAN Network"""
        self._listeners[listener.name] = listener

    def unregister(self, name: str) -> None:
        """remove a listener from the CAN network by its name identifier"""
        if name in self._listeners:
            self._listeners.pop(name)

    @property
    def listeners(self):
        return self._listeners

    def on_start(self):
        """create a mainloop that iterates through the recv poll generator

        NOTE: this doesn't use on_poll do to timing issues that occur in the
        time.sleep

        TODO: make component accept None sampling frequency and bypass the
        time.sleep call?
        """
        while not self.stopped:
            ret = self.recv(timeout=self.POLL_RECV_TIMEOUT)


class CanUdpNetwork(CanNetwork):
    """
    UDP Can Bus Implementation of Can Network

    Implements the CanNetwork interface for the UDPBus of python can
    """
    def __init__(self, name: str, port: int, ip: str,
                 whitelist: NetworkListType = None,
                 blacklist: NetworkListType = None,
                 do_bind: bool = True):
        super().__init__(name)
        self.port = port
        self.ip = ip
        self.bus = UDPBus(self.port, self.ip,
                          whitelist=whitelist, blacklist=blacklist, do_bind=do_bind)

    def send(self, can_id: int, data: CanDataType):
        if isinstance(data, str):
            data = bytearray(data.encode())
        msg = Message(arbitration_id=can_id, data=data, is_extended_id=True)
        self.bus.send(msg)

    def recv(self, timeout=None) -> typ.Union[None, typ.Tuple[int, Message]]:
        msg: Message = self.bus.recv(timeout=timeout)
        if msg:
            can_id, data, data_len = msg.arbitration_id, msg.data, msg.dlc
            for k, v in self._listeners.items():
                v.recv(can_id, data_len, data)
            return can_id, msg

    @property
    def blacklist(self):
        return self.bus.blacklist

    @blacklist.setter
    def blacklist(self, bl):
        self.bus.blacklist = bl

    @property
    def whitelist(self):
        return self.bus.whitelist

    @whitelist.setter
    def whitelist(self, wl):
        self.bus.whitelist = wl


class CanMultiverse(CanNetwork):
    """
    Multi-Network (Mux) of Can Networks

    Accepts a sequence of CanNetwork objects and implements a select method
    to switch to the active network. The interface functions are forwarded to
    the active network.
    """
    def __init__(self,
                 name: str,
                 networks: typ.Sequence[CanNetwork],
                 default_network: typ.Any):
        super(CanMultiverse, self).__init__(name)
        self._networks = networks
        assert len(networks) > 0, f"networks list is empty!"
        self._active_network = networks[0]
        self.select(default_network)

    def select(self, keyname: typ.Any) -> None:
        if keyname not in self.networks:
            raise ValueError(f"Selected network {keyname} doesn't exist")
        self._active_network = self.networks[keyname]

    def send(self, can_id: int, data: CanDataType) -> None:
        self._active_network.send(can_id, data)

    def recv(self, timeout=None) -> typ.Union[None, typ.Tuple[int, Message]]:
        ret = self._active_network.recv(timeout=timeout)
        if ret:
            cid, msg = ret
            for k, v in self._listeners.items():
                v.recv(cid, msg.dlc, msg.data)
            return cid, msg

    @property
    def networks(self):
        return {n.name: n for n in self._networks}
