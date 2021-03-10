'''
Project: SSITH CyberPhysical Demonstrator
Name: singleton.py
Author: Steven Osborn
Date: 25 August 2020

Threadsafe Singleton base class
'''

import threading

lock = threading.Lock()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            with lock:
                if cls not in cls._instances:
                    cls._instances[cls] = \
                        super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
