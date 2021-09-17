#! /usr/bin/env python3
"""
Project: SSITH CyberPhysical Demonstrator
Name: kiosk-backend.py
Author: Ethan Lew <elew@galois.com>, Michal Podhradsky <mpodhradsky@galois.com>, Steven Osborn <steven@lolsborn.com>, 
Date: 16 June 2021

"""
DEFAULT_NETWORK_CONFIG_PATH = "/home/pi/BESSPIN-Tool-Suite/besspin/base/utils/setupEnv.json"

if __name__ == "__main__":
    # Project libs
    from cyberphyslib.kiosk import kiosk
    from cyberphyslib.demonstrator import config
    import pathlib, os
    import argparse

    # ugh, this filepath access is sketchy and will complicate the deployment of ignition
    parser = argparse.ArgumentParser(description="BESSPIN Demonstrator Kiosk Backend")
    parser.add_argument("--network-config", type=str, default=DEFAULT_NETWORK_CONFIG_PATH, help="Path to BESSPIN Target setupEnv.json")
    parser.add_argument("--draw-graph", action='store_true', help="Generate transitions graph and exit")
    parser.add_argument("--deploy-mode", action='store_true', help="Start in deploy mode (can be switched later)")
    args = parser.parse_args()
    network_filepath = pathlib.Path(os.path.realpath(args.network_config))
    assert os.path.exists(network_filepath), f"specified network config json ({network_filepath}) doesn't exist"
    dnc = config.DemonstratorNetworkConfig.from_setup_env(network_filepath)
    kiosk = kiosk.HackerKiosk(dnc,deploy_mode=args.deploy_mode, draw_graph=args.draw_graph)
    if args.draw_graph:
        print("Drawing transitions graph.")
        kiosk.draw_graph("../../specs/state_machine_hacker_kiosk_implemented.png")
    else:
        print("Starting application.")
        kiosk.run()
