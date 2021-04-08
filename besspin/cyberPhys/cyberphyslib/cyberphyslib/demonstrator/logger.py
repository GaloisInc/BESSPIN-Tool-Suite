"""
Project: SSITH CyberPhysical Demonstrator
Name: logging.py
Author: Steven Osborn <steven@lolsborn.com>, Ethan Lew <elew@galois.com>
Date: 01 January 2021

Logs for Cyberphys Components
"""
import pathlib, os

import logging.config

# load utils/logging.conf
logging_filepath = pathlib.Path(os.path.realpath(__file__)).parent / "utils" / "logging.conf"
print(logging_filepath)
logging.config.fileConfig(logging_filepath)

# create logger objects
root_logger: logging.Logger = logging.getLogger('root')
can_logger: logging.Logger = logging.getLogger("can")
sim_logger: logging.Logger = logging.getLogger("sim")
speedo_logger: logging.Logger = logging.getLogger("speedo")
info_logger: logging.Logger = logging.getLogger("info_mux")
ssith_button_logger: logging.Logger = logging.getLogger("ssith-button")
led_manage_logger: logging.Logger = logging.getLogger("led_manage")
ignition_logger: logging.Logger = logging.getLogger("ignition")



