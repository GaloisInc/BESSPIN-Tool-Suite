"""
Project: SSITH CyberPhysical Demonstrator
Name: can.py
Author: Steven Osborn <steven@lolsborn.com>, Ethan Lew <elew@galois.com>
Date: 26 August 2020

CAN Packet encoder / decoder
"""
import abc
import typing as typ
import enum
from abc import ABCMeta, abstractmethod
from can import Message
from .component import ThreadExiting, Component

# TODO: @ethanlew import canlib/python/canlib.py properly
from cyberphyslib.canlib import CanDataType, UdpBus


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

    Implements the CanNetwork interface for the UdpBus of python can
    """
    def __init__(self, name: str, port: int, ip: str,
                 whitelist= None,
                 blacklist= None,
                 do_bind: bool = True):
        super().__init__(name)
        self.port = port
        self.ip = ip
        self.bus = UdpBus(self.port, self.ip,
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


import cyberphyslib.demonstrator.message as message
import cyberphyslib.demonstrator.config as config


class CanMultiverseStatus(enum.IntEnum):
    READY = enum.auto()
    ERROR = enum.auto()


class CanMultiverseComponent(Component):
    def __init__(self, ip_addr=None):
        super().__init__("canm", [(5050, "canm-commands")], [(5051, "canm-events")])
        sip = config.SIM_IP if not ip_addr else ip_addr
        can_ssith_info = CanUdpNetwork("secure_infotainment", config.CAN_PORT, sip)
        can_ssith_ecu = CanUdpNetwork("secure_ecu", config.CAN_PORT, sip)
        can_base = CanUdpNetwork("base", config.CAN_PORT, sip)
        networks = [can_base, can_ssith_ecu, can_ssith_info]

        can_ssith_info.whitelist = config.SSITH_INFO_WHITELIST
        can_ssith_ecu.whitelist = config.SSITH_ECU_WHITELIST
        can_base.whitelist = config.BASE_WHITELIST
        can_ssith_info.blacklist = config.SSITH_INFO_BLACKLIST
        can_ssith_ecu.blacklist = config.SSITH_ECU_BLACKLIST
        can_base.blacklist = config.BASE_BLACKLIST

        # create can network multiverse (mux)
        self._can_multiverse = CanMultiverse("multiverse", networks, default_network="base")

    def on_start(self):
        self._can_multiverse.start()

    def on_exit(self):
        self._can_multiverse.exit()

    # TODO: FIXME
    @recv_topic("canm-commands")
    def _(self, msg, t):
        if msg in CanMultiverseStatus:
            print("Received Message")
            #self._can_multiverse.select(msg.value)
            #self.send_message(message.Message(CanMultiverseStatus.READY), "canm-events")
        else:
            self.send_message(message.Message(CanMultiverseStatus.ERROR), "canm-events")
