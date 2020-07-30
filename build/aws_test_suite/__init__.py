"""
TODO:
    1. Address TODOs (esp. in aws_tools.py)
    2. Use typing module for type hints
    3. More error handling
    4. Test
"""

"""
FETT CI Library
"""
from .logger import console
from .aws_credentials import AWSCredentials
from .instance_manager import *
from .userdata_creator import UserdataCreator
