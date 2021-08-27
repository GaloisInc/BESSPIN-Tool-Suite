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

# create buses for both the can (udp) and cc (tcp) buses
print("Starting the CAN bus")
udp_net = cycan.CanUdpNetwork("udp-net", dnc.port_network_canbusPort, dnc.ip_SimPc)
tcp_net = cycan.CanTcpNetwork("tcp-net", dnc.port_network_canbusPort, dnc.ip_SimPc)
udp_net.start()
tcp_net.start()

# start everything up
hm = cyhealth.HeartbeatMonitor(udp_net)
hm.setup_can()
hm.setup_cc()
hm.start_monitor()
hm.mainloop()