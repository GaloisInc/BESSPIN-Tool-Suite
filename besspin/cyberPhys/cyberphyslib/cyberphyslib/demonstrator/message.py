"""
Project: SSITH CyberPhysical Demonstrator
Name: message.py
Author: Ethan Lew <elew@galois.com>
Date: 01 January 2021

Messaging for Cyberphys components
"""
import pickle
import time
import enum


class MessageLevel(enum.Enum):
    """
    Types of Messages
    """
    DEBUG = -1
    NORMAL = 0
    HIGH_FREQ = enum.auto()
    WARNING = enum.auto()
    URGENT = enum.auto()
    ERROR = enum.auto()


class Message:
    """
    Message is a data object shared between components
    """
    @staticmethod
    def serialize(msg):
        return pickle.dumps(msg)

    @staticmethod
    def deserialize(bmsg):
        return pickle.loads(bmsg)

    def __init__(self, msg: object, args=None, kwargs=None):
        """
        :param msg: must be pickable, and have a notion of equality
        :param args: optional arguments for message
        :param kwargs: option keyword arguments for message
        """
        self._msg = msg
        self.args = args
        self.kwargs = kwargs

    def __eq__(self, other):
        try:
            return self._msg == other
        except:
            return False

    def __bytes__(self):
        return self.serialize(self)

    def __str__(self):
        return str(self._msg)

    def __repr__(self):
        return self.__str__()

    @property
    def message(self):
        return self._msg


class Envelope:
    """
    Envelope provides context data for messages passed bewteen components
    """
    @staticmethod
    def serialize(msg):
        return pickle.dumps(msg)

    @staticmethod
    def deserialize(bmsg):
        return pickle.loads(bmsg)

    @classmethod
    def with_message(cls, component, level, *args, **kwargs):
        msg = Message(*args, **kwargs)
        return cls(component, msg, level=level)

    def __init__(self, component, msg, level=MessageLevel.NORMAL):
        self._level = level
        self._from = component.name
        self._create_time = time.time()
        self._msg = msg

    @property
    def message(self):
        return self._msg

    @property
    def sender_name(self):
        return self._from

    @property
    def send_time(self):
        return self._create_time

    @property
    def level(self):
        return self._level

    def __bytes__(self):
        return self.serialize(self)
