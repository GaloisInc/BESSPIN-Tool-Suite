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
        def _recv_ack(sn):
            poller = zmq.Poller()
            poller.register(sn, flags=zmq.POLLIN)
            if poller.poll(timeout=self.timeout):
                topic = sn.recv_string()
                recv: bytes = sn.recv_pyobj()
                env: Envelope = Envelope.deserialize(recv)
                mss = env.message
                sn.close()
                self.ret = mss

        self.context = zmq.Context()
        self.recv_socket: zmq.Socket = self.context.socket(zmq.SUB)
        self.recv_socket.connect(self.resource)
        self.recv_socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        self.recv = threading.Thread(target=_recv_ack, args=(self.recv_socket,), daemon=True)
        self.recv.start()

    def recv_message(self):
        self.recv.join()
        return self.ret

    def term(self):
        self.recv_socket.close()
        self.context.term()


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

    def start_component(self, comp: component.Component, wait=True):
        keyword = comp.name
        ignition_logger.info(f"Handler: Launching Service {keyword}...")
        if wait:
            comp.start()
            self._services[keyword] = comp
            return comp.wait_ready_command()
        else:
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

    def exit(self):
        # cast to list as _services will change in size
        for name in list(self._services.keys()):
            ignition_logger.info("Handler: Termination signal received!")
            self.stop_component(name)

    @property
    def components(self):
        return [s for _, s in self._services.items()]

    def __getitem__(self, key):
        return self._services[key]

