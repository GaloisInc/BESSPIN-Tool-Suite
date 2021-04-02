#!/usr/env/python3
"""
Project: SSITH CyberPhysical Demonstrator
Name: ignition.py
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Date: 05 January 2021

usage: ignition.py [-h] [--can-apply-lists | --no-can-apply-lists]
                   [--can-select-keystroke-mux | --no-can-select-keystroke-mux]
                   [--use-speedo | --no-use-speedo]
                   [--use-led-manager | --no-use-led-manager]
                   [--can-ip CAN_IP]

Demonstrator Simulation Application

optional arguments:
  -h, --help            show this help message and exit
  --can-apply-lists     Apply network blacklists/whitelists provided in
                        cyberphys.config for the can networks
  --no-can-apply-lists  [NOT] Apply network blacklists/whitelists provided in
                        cyberphys.config for the can networks
  --can-select-keystroke-mux
                        Create a 'keystroke mux' to change active CAN network
                        (use ctrl+f7 to change active network)
  --no-can-select-keystroke-mux
                        [NOT] Create a 'keystroke mux' to change active CAN
                        network (use ctrl+f7 to change active network)
  --use-speedo          Use the speedometer component (turn off when the
                        speedometer is unconnected)
  --no-use-speedo       [NOT] Use the speedometer component (turn off when the
                        speedometer is unconnected)
  --use-led-manager
                        Use the LED manager (turn off when the LED hardware
                        isn't connected)
  --no-use-led-manager
                        [NOT] Use the LED manager (turn off when the LED
                        hardware isn't connected)
  --can-ip CAN_IP       Use argument ip instead of SIM_IP in cyberphys.config
"""

# Python standard libraries
import time
import platform
import signal
import argparse

# Project libs
from cyberphyslib.demonstrator import (can, config, simulator,
                       logger, mux, infotainment, can_out)

SSITH_ENABLED = False
BUFFER_SIZE = 1024

# Exit codes
WRONG_OS = 10
NO_BEAMNG = 20


def attempt_force_quit():
    """look for BeamNG component threads and attempt to exit them"""
    logger.root_logger.warning("attempting a force quit from ignition")
    attempt_threads = ["can_multiverse", "speedo", "beamng_sim", "ledm", "info_net", "location_poller"]

    def force_exit_component(component):
        # send signal to resources (exit) and force exit (_exit)
        logger.root_logger.warning(f"closing down {component.name}...")
        component.exit()
        component.join()
        logger.root_logger.warning(f"successfully closed {component.name}")

    for athread in attempt_threads:
        if athread in globals() and globals()[athread].is_alive():
            logger.root_logger.warning(f"found {athread} to force quit")
            force_exit_component(globals()[athread])


class DelayedKeyboardInterrupt(object):
    """annotate code that cannot be stopped by SIGINTs"""
    def __enter__(self):
        self.signal_received = False
        self.old_handler = signal.signal(signal.SIGINT, self.handler)

    def handler(self, sig, frame):
        self.signal_received = (sig, frame)
        logger.root_logger.debug('SIGINT received. Delaying KeyboardInterrupt.')

    def __exit__(self, type, value, traceback):
        signal.signal(signal.SIGINT, self.old_handler)
        if self.signal_received:
            self.old_handler(*self.signal_received)


# create argparser
def add_bool_grp(parser: argparse.ArgumentParser, var_name: str,
                 default: bool=True, help: str=''):
    """create pairs of input arguments that assigns a boolean in the argument parser
    :param parser: parser to affect
    :param var_name: variable (argument) to add
    :param default: default boolean state when unspecified
    :param help: help string to assign to the pairs
    """
    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument(f'--{var_name}', dest=var_name.replace("-", "_"), action='store_true', help=help)
    feature_parser.add_argument(f'--no-{var_name}', dest=var_name.replace("-", "_"), action='store_false', help=f"[NOT] {help}")
    parser.set_defaults(**{var_name.replace("-", "_"):default})


parser = argparse.ArgumentParser(description=f"Demonstrator Simulation Application")
add_bool_grp(parser, "can-apply-lists", default=True, help="Apply network blacklists/whitelists provided"
                                                            f" in cyberphys.config for the can networks")
add_bool_grp(parser, "can-select-keystroke-mux", default=True, help="Create a 'keystroke mux' to change active "
                                                  f"CAN network (use ctrl+f7 to change active network)")
add_bool_grp(parser, "use-speedo", default=True, help="Use the speedometer component (turn off when the "
                                                  f"speedometer is unconnected)")
add_bool_grp(parser, "use-led-manager", default=True, help="Use the LED manager (turn off when the LED hardware "
                                                               f"isn't connected)")
parser.add_argument("--can-ip", type=str, help="Use argument ip instead of SIM_IP in cyberphys.config")
args = parser.parse_args()


# Ensure we're running this on a windows machine
if platform.system() != "Windows":
    logger.root_logger.error("Ignition must happen on Windows PC along \
                 where simulator lives.\n Exiting...")
    exit(WRONG_OS)                                             

# Start the BeamNG simulator as a thread
beamng_sim = simulator.Sim()

# Spin up speedometer code as a thread.
# If this code fails it should log the reason and the thread will exit,
# but will not cause the whole simulation to tank.
if args.use_speedo:
    import cyberphys.speedometer as speedometer
    speedo = speedometer.Speedo()
else:
    logger.speedo_logger.info(f"Not using speedometer as disabled by input argument")

# start the LED manager
if args.use_led_manager:
    import cyberphys.leds_manage as leds_manage
    # TODO: hard-coded path
    ledmanager = leds_manage.LedManagerComponent.from_csv("../cyberphyslib/demonstrator/utils/led_strings_comprehensive_tuple_colors.csv")
else:
    logger.led_manage_logger.info(f"Not using LED manager as disabled by input argument")

# Start-up the SSITH / Baseline CAN networks
sip = config.SIM_IP if not args.can_ip else args.can_ip
can_ssith_info = can.CanUdpNetwork("secure_infotainment", config.CAN_PORT, sip)
can_ssith_ecu = can.CanUdpNetwork("secure_ecu", config.CAN_PORT, sip)
can_base = can.CanUdpNetwork("base", config.CAN_PORT, sip)
networks = [can_base, can_ssith_ecu, can_ssith_info]

# apply can lists
if args.can_apply_lists:
    can_ssith_info.whitelist = config.SSITH_INFO_WHITELIST
    can_ssith_ecu.whitelist = config.SSITH_ECU_WHITELIST
    can_base.whitelist = config.BASE_WHITELIST
    can_ssith_info.blacklist = config.SSITH_INFO_BLACKLIST
    can_ssith_ecu.blacklist = config.SSITH_ECU_BLACKLIST
    can_base.blacklist = config.BASE_BLACKLIST
else:
    logger.can_logger.info("Not applying whitelists/blacklists as disabled by input argument")

# create can network multiverse (mux)
can_multiverse = can.CanMultiverse("multiverse", networks, default_network="base")

# Example CAN network listener.  This will recieve
# packets from the selected network only
example_listener = can.ExampleListener()
can_multiverse.register(example_listener)
can_multiverse.register(beamng_sim)

# Start the infotainment mux
info_net = can.CanUdpNetwork("info-net", config.INFO_UI_PORT, sip)
imux = infotainment.InfotainmentProxy(info_net, can_multiverse)

# Will poll vehicle location and transmit via CAN
location_poller = can_out.CanOutPoller(can_multiverse)

# for now, show the security mode feature and that the multiverse works for each scenario by registering a "keystroke mux"
# (keystroke) to toggle through the networks
if args.can_select_keystroke_mux:
    logger.root_logger.info("Initializing SSITH Security Mux")
    def keystroke_mux_cb(state_enabled):
        name = networks[state_enabled].name
        logger.root_logger.info(f"switching to network {name}")
        can_multiverse.select(name)
    sb = mux.CallbackButton(callback=keystroke_mux_cb, nstates=len(networks))

try:
    # start the components
    beamng_sim.start()
    if args.use_speedo:
        speedo.start()
    can_multiverse.start()
    if args.use_led_manager:
        ledmanager.start()
    info_net.start()
    location_poller.start()

    # loop while component threads are used
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    with DelayedKeyboardInterrupt():
        attempt_force_quit()
except Exception as exc:
    logger.root_logger.warning(f"Caught exception <{exc}>. Will attempt to exit threads")
    with DelayedKeyboardInterrupt():
        attempt_force_quit()
