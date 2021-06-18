import argparse
from cyberphyslib.demonstrator import can
import cyberphyslib.canlib as canlib

import logging
import struct
# make CAN module less noisy
logging.getLogger("can").setLevel(logging.WARNING)


class StatsListener(can.CanListener):
    canids = {getattr(canlib, name):name.split('CAN_ID_')[1] for name in dir(canlib) if 'CAN_ID' in name}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vals = set()
        self.count = 0

    def recv(self, id: int, data_len: int, data: bytes):
        if id in self.canids:
            val = (self.canids[id],
                   struct.unpack(
                       getattr(canlib, f"CAN_FORMAT_{self.canids[id]}"), data)
                   )
            self.vals |= {val}
            self.count += 1
            print(f"{name}: {self.ids_recv}")

    @property
    def ids_recv(self):
        return set([v for v,_ in self.vals])

    def get_vals(self, id):
        return set([v for k,v in self.vals if k == id])


class StatsNetwork:
    def __init__(self, name, ip, port, whitelist):
        self.can_net = can.CanUdpNetwork(name, port, ip, whitelist=whitelist)
        self.listener = StatsListener(name)
        self.can_net.register(self.listener)


    def start(self):
        self.can_net.start()

if __name__ == '__main__':
    # Project libs
    from cyberphyslib.demonstrator import config
    import pathlib, os
    import argparse

    # ugh, this filepath access is sketchy and will complicate the deployment of ignition
    parser = argparse.ArgumentParser(description="BESSPIN Demonstrator Can Check")
    parser.add_argument("-network-config", type=str, default="", help="Path to BESSPIN Target setupEnv.json")
    parser.add_argument("-network-port-name", type=str, default="canbus", help="Network Port Name")
    args = parser.parse_args()
    if args.network_config == "":
        network_filepath = pathlib.Path(os.path.realpath(__file__)).parent / ".." / ".." / "base" / "utils" / "setupEnv.json"
    else:
        network_filepath = args.network_config
    assert os.path.exists(network_filepath), f"specified network config json ({network_filepath}) doesn't exist"
    dnc = config.DemonstratorNetworkConfig.from_setup_env(network_filepath)

    name = args.network_port_name
    port = dnc.network_ports[f'{name}Port']
    whitelists = dnc.whitelists
    nets = [StatsNetwork(f"{net_name}_STATS", dnc.ip_SimPc, port, wl) for net_name, wl in whitelists.items()]
    for net in nets:
        net.start()
    while True:
        pass
