"""
Project: SSITH CyberPhysical Demonstrator
handler.py
Author: Ethan Lew <elew@galois.com>
Date: 04/05/2021
Python 3.8.3
O/S: Windows 10

Manage the demonstrator program flow

TODO: add more docstrings
"""
from cyberphyslib.demonstrator import component
from cyberphyslib.demonstrator.message import Envelope, MessageLevel, Message
from cyberphyslib.demonstrator.logger import ignition_logger
import threading
import zmq


class SubSocket:
    """zmq SUB recv thread context manager"""
    def __init__(self, resource, topic, timeout=60000):
        self.resource = resource
        self.topic = topic
        self.recv = None
        self.ret = None
        self.timeout = timeout

    def start(self):
        def _recv(resource, topic, evt):
            context = zmq.Context()
            socket = context.socket(zmq.PAIR)
            socket.connect(resource)
            evt.set()
            socket.recv_string()
            recv = socket.recv_pyobj()
            env = Envelope.deserialize(recv)
            mss = env.message
            self.ret = mss
            socket.close()
            context.term()
        ready = threading.Event()
        self.recv = threading.Thread(target=_recv, args=(self.resource, self.topic, ready), daemon=True)
        #import time
        #while not ready.is_set():
        #    time.sleep(0.1)
        self.recv.start()
        #def _recv_ack(sn):
        #    poller = zmq.Poller()
        #    poller.register(sn, flags=zmq.POLLIN)
        #    if poller.poll(timeout=self.timeout):
        #        topic = sn.recv_string()
        #        recv: bytes = sn.recv_pyobj()
        #        env: Envelope = Envelope.deserialize(recv)
        #        mss = env.message
        #        sn.close()
        #        self.ret = mss

        #self.context = zmq.Context()
        #self.recv_socket: zmq.Socket = self.context.socket(zmq.SUB)
        #self.recv_socket.connect(self.resource)
        #self.recv_socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        #self.recv = threading.Thread(target=_recv_ack, args=(self.recv_socket,), daemon=True)
        #self.recv.start()

    def recv_message(self):
        self.recv.join()
        return self.ret

    def term(self):
        #self.recv_socket.close()
        #self.context.term()
        pass


class SubSocketManager:
    def __init__(self, resource, topic):
        self.resource = resource
        self.topic = topic
        self._ssock = SubSocket(resource=self.resource, topic=self.topic)
        self._ssock.start()

    def __enter__(self):
        return self._ssock

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._ssock.term()


class ComponentHandler:
    """componentHandler manages ignition components,

    1. create components
    2. connect to components
    3. communicate with components

    TODO: logger
    """
    def __init__(self, ip_addr = "127.0.0.1"):
        self._services = {}
        self._command_entry = {}
        self._events_entry = {}
        self._zmq_context = zmq.Context()
        self.name = "SERVICE"
        self.out_sock = None
        self.ip_addr = ip_addr

    def connect_component(self, port_input, port_output, component_name):
        """
        TODO: accept component_cls instead of keyword
        """
        # TODO: weird
        if not self.out_sock:
            self.out_sock = self._zmq_context.socket(zmq.PUB)
            self.out_sock.bind(f"tcp://*:{port_output}")

        self._events_entry[component_name] = (port_input, component_name)
        self._command_entry[component_name] = self.out_sock

    def disconnect_component(self, component_name):
        if component_name in self._events_entry and component_name in self._command_entry:
            v = self._command_entry[component_name]
            v.close()
            del self._command_entry[component_name]
            del self._events_entry[component_name]

    def start_component(self, comp: component.Component, wait=True):
        keyword = comp.name
        ctopic, etopic = f"{comp.name}-commands", f"{comp.name}-events"
        porto = {t: p for p, t in comp._in_ports}.get(ctopic, None)
        porti = {t: p for p, t in comp._out_ports}.get(etopic, None)
        ignition_logger.info(f"Handler: Launching Service {keyword}...")
        if wait:
            with SubSocketManager(f"tcp://{self.ip_addr}:{porti}", etopic) as ssock:
                self.connect_component(porti, porto, keyword)
                comp.start()
                self._services[keyword] = comp
                return ssock.recv_message()
        else:
            self.connect_component(porti, porto, keyword)
            comp.start()
            self._services[keyword] = comp

    def stop_component(self, keyword):
        if keyword not in self._services:
            ignition_logger.info(f"Handler: {keyword} is not in ({set(self._services.keys())}) started services")
            return
        else:
            ignition_logger.info(f"Handler: closing down {keyword}...")
            self._services[keyword].exit()
            self._services[keyword].join()
            del self._services[keyword]

    def message_component(self, component_kw, message, do_receive=True):
        if do_receive:
            porti, topic = self._events_entry[component_kw]
            with SubSocketManager(f"tcp://{self.ip_addr}:{porti}", f"{component_kw}-events") as sub_sock:

                self._command_entry[component_kw].send_string(f"{component_kw}-commands", zmq.SNDMORE)
                self._command_entry[component_kw].send_pyobj(Envelope.serialize(Envelope(self,
                                                                                         Message(message),
                                                                                         level=MessageLevel.NORMAL)))
                return sub_sock.recv_message()
        else:
            self._command_entry[component_kw].send_string(f"{component_kw}-commands", zmq.SNDMORE)
            self._command_entry[component_kw].send_pyobj(Envelope.serialize(Envelope(self,
                                                                                     Message(message),
                                                                                     level=MessageLevel.NORMAL)))

    def exit(self):
        for _, v in self._command_entry.items():
            v.close()

        if self._zmq_context is not None:
            self._zmq_context.term()

        # cast to list as _services will change in size
        for name in list(self._services.keys()):
            ignition_logger.info("Handler: Termination signal received!")
            self.stop_component(name)

    @property
    def components(self):
        return [s for _, s in self._services.items()]
