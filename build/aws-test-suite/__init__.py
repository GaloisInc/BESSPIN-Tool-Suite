"""
FETT CI Library
"""
from .workgroup import *


def setup_logger(log_fname="cilib.log", level="info"):
    """global logger setup"""
    # empty out log file
    open(log_fname, 'w').close()
    import logging
    llevel = {"critical" : logging.CRITICAL, "error" : logging.ERROR,
                      "warning" : logging.WARNING, "info" : logging.INFO,
                      "debug" : logging.DEBUG, "notset" : logging.NOTSET}
    log_level = llevel[level]
    logging.basicConfig(format='%(asctime)s: (%(levelname)s)  %(message)s', datefmt='%I:%M:%S %p', level=log_level,
                            handlers=[logging.FileHandler(log_fname), logging.StreamHandler()])
    logging.info(f"CI Lib Logger Initialized\nLog File: {log_fname}\nLog Level: {level}")