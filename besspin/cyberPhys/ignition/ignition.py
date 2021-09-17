#!/usr/env/python3
"""
Project: SSITH CyberPhysical Demonstrator
Name: ignition.py
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Date: 15 April 2021

"""
import time

if __name__ == "__main__":
    # Project libs
    from cyberphyslib.demonstrator import director
    from cyberphyslib.demonstrator import config
    import pathlib, os
    import argparse

    # ugh, this filepath access is sketchy and will complicate the deployment of ignition
    parser = argparse.ArgumentParser(description="BESSPIN Demonstrator Ignition")
    parser.add_argument("-network-config", type=str, default="", help="Path to BESSPIN Target setupEnv.json")
    parser.add_argument("-race-car", action='store_true', help="Use the race car")
    args = parser.parse_args()
    if args.network_config == "":
        network_filepath = pathlib.Path(os.path.realpath(__file__)).parent / ".." / ".." / "base" / "utils" / "setupEnv.json"
    else:
        network_filepath = args.network_config
    assert os.path.exists(network_filepath), f"specified network config json ({network_filepath}) doesn't exist"
    dnc = config.DemonstratorNetworkConfig.from_setup_env(network_filepath)
    ignition = director.IgnitionDirector.from_network_config(dnc)
    if args.race_car:
        print("Enjoy the race car!")
        ignition.set_race_car(True)
    try:
        ignition.start()
    except KeyboardInterrupt:
        print("Ignition terminating")
        ignition.terminate()
    print("Ignition terminated")
