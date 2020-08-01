"""
TODO:
    . Documentation
        . logger.py
        . instance_manager.py
    . Address TODOs (esp. in aws_tools.py)
    . Use typing module for type hints
    . More error handling
    . Test
"""

"""
FETT CI Library
"""
from .logger import log
from .aws_credentials import *
from .instance_manager import *
from .userdata_creator import *
