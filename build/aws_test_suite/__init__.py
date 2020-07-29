"""
TODO:
    1. Documentation
        a. __init__.py
        b. aws_tools.py
    2. Use typing module for type hints
    3. More error handling
    4. Test
"""

"""
FETT CI Library
"""
from .ec2_work_group import *
from .aws_credentials import AWSCredentials
from .userdata_creator import UserdataCreator


def setup_logger(log_fname="aws-test-suite.log", level="info"):
    """global logger setup"""
    # empty out log file
    open(log_fname, 'w').close()
    import logging
    llevel = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "notset": logging.NOTSET
    }
    log_level = llevel[level]
    logging.basicConfig(format='%(asctime)s: (%(levelname)s)  %(message)s', datefmt='%I:%M:%S %p', level=log_level,
                        handlers=[logging.FileHandler(log_fname), logging.StreamHandler()])
    logging.info(f"AWS Test Suite Logger Initialized\nLog File: {log_fname}\nLog Level: {level}")
