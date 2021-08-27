import cyberphyslib.demonstrator.health as cyhealth
import cyberphyslib.demonstrator.config as cyconfig
import cyberphyslib.demonstrator.can as cycan

from cyberphyslib.demonstrator import director
from cyberphyslib.demonstrator import config
import pathlib, os
import argparse

# ugh, this filepath access is sketchy and will complicate the deployment of ignition
parser = argparse.ArgumentParser(description="BESSPIN Demonstrator Ignition")
parser.add_argument("-network-config", type=str, default="", help="Path to BESSPIN Target setupEnv.json")
args = parser.parse_args()
if args.network_config == "":
    network_filepath = pathlib.Path(
        os.path.realpath(__file__)).parent / ".." / ".." / "base" / "utils" / "setupEnv.json"
else:
    network_filepath = args.network_config
assert os.path.exists(network_filepath), f"specified network config json ({network_filepath}) doesn't exist"
dnc = config.DemonstratorNetworkConfig.from_setup_env(network_filepath)

print("Starting the CAN bus")
net = cycan.CanUdpNetwork("name", dnc.port_network_canbusPort, dnc.ip_SimPc)
net.start()

hm = cyhealth.HeartbeatMonitor(net)
hm.setup_can()
hm.start_monitor()

while True:
    pass