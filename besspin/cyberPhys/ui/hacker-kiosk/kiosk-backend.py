#!/usr/env/python3
"""
Project: SSITH CyberPhysical Demonstrator
Name: kiosk-backend.py
Author: Ethan Lew <elew@galois.com>, Michal Podhradsky <mpodhradsky@galois.com>, Steven Osborn <steven@lolsborn.com>, 
Date: 16 June 2021

"""
if __name__ == "__main__":
    # Project libs
    from cyberphyslib.kiosk import director
    from cyberphyslib.demonstrator import config
    import pathlib, os
    import argparse

    # ugh, this filepath access is sketchy and will complicate the deployment of ignition
    parser = argparse.ArgumentParser(description="BESSPIN Demonstrator Kiosk Backend")
    parser.add_argument("-network-config", type=str, default="", help="Path to BESSPIN Target setupEnv.json")
    args = parser.parse_args()
    if args.network_config == "":
        network_filepath = pathlib.Path(os.path.realpath(__file__)).parent / ".." / ".." / "base" / "utils" / "setupEnv.json"
    else:
        network_filepath = args.network_config
    assert os.path.exists(network_filepath), f"specified network config json ({network_filepath}) doesn't exist"
    dnc = config.DemonstratorNetworkConfig.from_setup_env(network_filepath)
    #kiosk = director.HackerKiosk.for_besspin(dnc)
    kiosk = director.HackerKiosk()
    kiosk.draw_graph("kiosk-backend-transitions.png")
    kiosk.run()

