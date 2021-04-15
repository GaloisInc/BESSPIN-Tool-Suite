"""
Project: SSITH CyberPhysical Demonstrator
Name: component.py
Author: Ethan Lew
Date: 02 October 2020

an object to establish communication and messaging between services

pub/sub approach -- establish service subscribers and publishers at
initialization. register topics and callbacks for service components.
"""
from .message import Message, Envelope, MessageLevel

import threading
import typing as typ
import zmq
import time
import enum
import functools
import collections
import struct


class ComponentStatus(enum.Enum):
    """component states and commands"""
    READY = enum.auto()
    ERROR = enum.auto()


class ComponentPollerStatus(enum.Enum):
    """component poller states"""
    POLLER_START = enum.auto()
    POLLER_END = enum.auto()


def coroutine(func):
    """decorator for coroutine creation/initialization"""
    @functools.wraps(func)
    def primer(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return primer


class ComponentMetaDict(dict):
    """resolve overloaded attributes"""
    def __setitem__(self, key, value):
        if hasattr(value, 'recv_spec'):
            if "_recv_methods" not in self:
                self["_recv_methods"] = {}
            self["_recv_methods"][getattr(value, 'recv_spec')] = value
        elif hasattr(value, 'recv_can_spec'):
            if "_recv_can_methods" not in self:
                self["_recv_can_methods"] = {}
            self["_recv_can_methods"][getattr(value, 'recv_can_spec')] = value
        else:
            super().__setitem__(key, value)

    def _getitem__(self, key):
        if key not in self and '_' and key.isupper():
            return key.upper()
        else:
            return super().__getitem__(key)


class ComponentMeta(type):
    """recognize special decorators, and build out the implied attributes"""
    @classmethod
    def __prepare__(metacls, name, bases):
        def _register_can(*args):
            recv_spec = args
            def decorate(func):
                func.recv_can_spec = recv_spec
                return func
            return decorate

        def _register_topic(*args):
            recv_spec = args
            def decorate(func):
                func.recv_spec = recv_spec
                return func
            return decorate
        d = ComponentMetaDict()
        d["recv_topic"] = _register_topic
        # TODO: add CAN registry in Component, which may not be the best place for it
        d["recv_can"] = _register_can
        return d

    @classmethod
    def _build(cls, attributes):
        pass

    def __new__(meta, clsname, bases, attributes):
        del attributes["recv_topic"]
        del attributes["recv_can"]
        cls = super().__new__(meta, clsname, bases, attributes)
        return cls


class ThreadExiting(threading.Thread):
    """ThreadExiting presents a thread associated with a stop event. Computations done by the
    thread are decomposed into poller initialization, polling iteration, and deinitialization.
    This permits the thread to stop gracefully, attending to resources used."""
    def __init__(self, name, *args, sample_frequency=60, **kwargs):
        super().__init__(name=name, *args, daemon=True, **kwargs)
        self.stop_evt = threading.Event()
        self.poller_start_time = None
        self.polling_thread = None
        self.sample_period = 1.0 / sample_frequency

    def on_poll(self, t):
        pass

    def on_start(self):
        pass

    def run(self):
        self.on_start()
        while not self.stopped:
            it_start = time.time()
            if self.poller_start_time is None:
                self.poller_start_time = time.time()
                t = self.poller_start_time
            else:
                t = time.time() - self.poller_start_time
            self.on_poll(t)
            it_end = time.time()
            it_diff = it_end - it_start
            if (self.sample_period - it_diff) > 0:
                time.sleep(self.sample_period - it_diff)
        self.on_exit()

    def on_exit(self):
        pass

    def stop(self):
        self.stop_evt.set()

    @property
    def stopped(self):
        return self.stop_evt.is_set()

    def exit(self):
        self.stop()
        self.join()


class Component(ThreadExiting, metaclass=ComponentMeta):
    def __init__(self, name: str,
                 in_descr: typ.List[typ.Tuple],
                 out_descr: typ.List[typ.Tuple],
                 *args,
                 ip_addr='127.0.0.1' ,
                 **kwargs):
        """
        :param in_descr: port description tuple (elements are of the form (port number, topic name))
        :param out_descr: port description tuple (elements are of the form (port number, topic name))
        """
        super(Component, self).__init__(name, *args, **kwargs)
        self.ip_addr = ip_addr

        self._in_ports: typ.Set[typ.Tuple] = set(in_descr)
        self._out_ports: typ.Set[typ.Tuple] = set(out_descr)

        self._name = name

        self._zmq_context: typ.Union[zmq.Context, None] = None
        self._in_socks: typ.List[zmq.socket.Socket] = []
        self._out_sock: typ.Union[zmq.socket.Socket, None] = None

        # time since initialization
        self._epoch = time.time()
        self._unbound = False
        self._ready = False

        # bind here so startup messages can be received
        self.bind()

    def send_message(self, message: Message, topic: str, level=MessageLevel.NORMAL) -> None:
        """send message over pub/sub network
        """
        assert self._out_sock is not None, f"requested to send message with no outgoing socket (None)"
        assert topic in self.out_topics, f"requested to send message with invalid topic {topic}"
        self._out_sock.send_string(topic, zmq.SNDMORE)
        self._out_sock.send_pyobj(Envelope.serialize(Envelope(self, message, level=level)))

    @coroutine
    def get_receiver(self):
        """create an iterable object that yields incoming messages"""
        # prime the coroutine
        yield None

        # main loop -- iterate through input sockets and yield incoming messages
        try:
            while not self.stopped:
                for sn in self._in_socks:
                    if self.stopped:
                        yield (f"{self.name}-command", Message(ComponentStatus.EXIT), None)
                    while  isinstance(sn, zmq.Socket) and sn.poll(1) == zmq.POLLIN:
                        topic = sn.recv_string(zmq.DONTWAIT)
                        recv: bytes = sn.recv_pyobj(zmq.DONTWAIT)
                        env: Envelope = Envelope.deserialize(recv)
                        msg = env.message
                        t = env.send_time
                        yield (topic, msg, t)
        except Exception as exc:
            # TODO: log here
            pass

    def on_recv(self, topic, msg, t) -> None:
        pass

    def _process_recvs(self, topic: str, msg: Message, t):
        """find reception response in the receiver registry"""
        rgy = self.recv_methods
        if (topic,) in rgy:
            rgy[(topic,)](self, msg, t)
        if isinstance(msg.message, collections.Hashable) and (topic, msg.message) in rgy:
            rgy[(topic, msg.message)](self, t)
        self.on_recv(topic, msg, t)

    def recv(self, id: int, data_len: int, data: bytes):
        """find reception response in the can receiver registry"""
        rgy = self.recv_can_methods
        if id in rgy:
            fmt = rgy[id][0]
            # use network order (!)
            msg = struct.unpack(fmt, bytearray(data)[:data_len])
            rgy[id][1](self, msg)

    @property
    def recv_methods(self):
        """get all registered receive components for self"""
        return getattr(self, "_recv_methods", {})

    @property
    def recv_can_methods(self):
        """get all registered receive components for self"""
        d = getattr(self, "_recv_can_methods", {})
        return {k[0]: (k[1], v) for k,v in d.items()}

    def run(self) -> None:
        """component mainloop"""
        self._ready = True
        recvr = self.get_receiver()
        self.on_start()
        for topic, msg, t in recvr:
            self._process_recvs(topic, msg, t)
            if self.stopped:
                break
        self.unbind()
        self.on_exit()

    def bind(self) -> None:
        """setup sockets"""
        if self._zmq_context is not None:
            self.unbind()

        self._zmq_context = zmq.Context()

        if len(self.out_topics) > 0:
            # assert that all out port nums are the same
            ports = set([i for i, _ in self._out_ports])
            assert len(
                ports) == 1, f"outgoing port numbers must all be the same for {self.__class__.__name__} (got {ports})"

            self._out_sock = self._zmq_context.socket(zmq.PUB)
            self._out_sock.bind(f"tcp://*:{list(self._out_ports)[0][0]}")

        for port, topic in self._in_ports:
            in_sock = self._zmq_context.socket(zmq.SUB)
            in_sock.connect(f"tcp://{self.ip_addr}:{port}")
            in_sock.setsockopt_string(zmq.SUBSCRIBE, topic)
            self._in_socks.append(in_sock)

        # give zmq time
        time.sleep(0.2)

    def unbind(self) -> None:
        """unbind/disconnect sockets, terminate zmq session"""
        self._unbound = True
        for idx, s in enumerate(self._in_socks):
            s.close()
            self._in_socks[idx] = None

        if self._out_sock is not None:
            self._out_sock.close()

        if self._zmq_context is not None:
            self._zmq_context.term()

        self._zmq_context = None
        self._in_socks = []
        self._out_sock = None

    @property
    def in_topics(self):
        return [i for _, i in self._in_ports]

    @property
    def out_topics(self):
        return [i for _, i in self._out_ports]

    @property
    def name(self):
        return self._name


class ComponentPoller(Component):
    """add a polling thread to respond at a given sampling frequency"""
    def __init__(self, *args, sample_frequency=60, **kwargs):
        super().__init__(*args, **kwargs)

        # poller properties
        self.polling_thread = ThreadExiting(name=f"{self.name}-poller", sample_frequency=sample_frequency, **kwargs)
        self.polling_thread.on_poll =  self.on_poll_poll
        self.polling_thread.on_start = self.on_poll_start
        self.polling_thread.on_exit = self.on_poll_exit
        self._call_started = False

    def on_poll_start(self):
        pass

    def on_poll_exit(self):
        pass

    def on_poll_poll(self, t):
        pass

    def start_poller(self):
        """start sensor polling thread"""
        if not self.stopped:
            self.polling_thread.start()
            self._call_started = True

    def stop_poller(self):
        """stop sensor polling thread"""
        if self._call_started:
            self.polling_thread.stop()

    def exit_poller(self):
        if self._call_started:
            self.polling_thread.exit()

    def stop(self):
        self.stop_poller()
        super().stop()

    def exit(self):
        self.exit_poller()
        super().exit()
