"""
Project: SSITH CyberPhysical Demonstrator
Name: config.py
Author: Steven Osborn <steven@lolsborn.com>, Ethan Lew <elew@galois.com>
Date: 01 January 2021

Cyberphys Demonstrator Configuration Variables
"""

# directory of ignition stations
RADIO_SOUND_DIR = r"C:\\sound"  # FIXME: commit songs to repo? (requires merge from infotainment-ui branch)

# port timeouts
SCENARIO_TIMEOUT = 5*60 # s
CC_TIMEOUT = 60 # s

# name of joystick for ignition to monitor
JOYSTICK_NAME = 'FANATEC Podium Wheel Base DD1'
# Uncomment for the thrustmaster t150 wheel
# JOYSTICK_NAME = 'Thrustmaster T150 Racing Wheel'

# See cyberPhys-test.ini for IP allocation
APPLY_LISTS = True

# position/heading margins of error before reporting changes
MIN_POSITION_CHANGE = 0.8
MIN_HEADING_CHANGE = 0.5

# for zeromq comms (localhost)
BEAMNG_SIM_PORT = 5014
DIRECTOR_PORT = 5015
SPEEDO_PORT = 5016
LED_MANAGE_PORT = 5017
CANM_PORT =  5018
INFO_PLAY_PORT = 5019
LOCATION_PORT = 5021
INFO_UI_PORT = 5022
JMONITOR_PORT = 5023
PMONITOR_PORT = 5024

LOCATION_POLL_HZ = 5

BEAMNG_SETTINGS_PATH_RELATIVE = r"\BeamNG.tech\settings\\"

BEAMNG_GAME_INI_FILE_NAME = r"game-settings.ini"
BEAMNG_GAME_CS_FILE_NAME = r"game-settings.cs"

BEAMNG_CYBERPHYS_INI_FILE_NAME = r"game-settings_cyberphys.ini"
BEAMNG_CYBERPHYS_CS_FILE_NAME = r"game-settings_cyberphys.cs"

BEAMNG_PORT=64256
BEAMNG_PATH=r"C:\BeamNG.tech"

# Override this if you need to change your user path. User path with spaces are not supported.
BEAMNG_USER_PATH=None
BEAMNG_OUTGAUGE_PORT = 4445 # Outgauge emulation

BEAMNG_COMPONENT_ELECTRIC = (BEAMNG_SIM_PORT, 'sensor-electric')
BEAMNG_COMPONENT_GFORCE   = (BEAMNG_SIM_PORT, 'sensor-gforce')
BEAMNG_COMPONENT_EVENTS   = (BEAMNG_SIM_PORT, 'beamng-events')
BEAMNG_COMPONENT_STATE    = (BEAMNG_SIM_PORT, 'beamng-state')
BEAMNG_COMPONENT_VEHICLE  = (BEAMNG_SIM_PORT, 'beamng-vehicle')
BEAMNG_COMPONENT_SENSORS  = (BEAMNG_SIM_PORT, "beamng-sensors")

# BeamNG service communication info
BEAMNG_COMPONENT_OUTPUT = [BEAMNG_COMPONENT_ELECTRIC,
                           BEAMNG_COMPONENT_GFORCE,
                           BEAMNG_COMPONENT_EVENTS,
                           BEAMNG_COMPONENT_STATE,
                           BEAMNG_COMPONENT_VEHICLE,
                           BEAMNG_COMPONENT_SENSORS
                          ]

BEAMNG_COMPONENT_INPUT = [(DIRECTOR_PORT, 'beamng-commands'),
                          (INFO_UI_PORT, 'infoui-beamng'),
                          (JMONITOR_PORT, 'jmonitor-beamng'),
                          (PMONITOR_PORT, 'pmonitor-beamng')]

# keyword arguments to pass to Vehicle when creating a vehicle for the sim scenario
BEAMNG_VEHICLE_CONFIG = {"model" : "etk800", "partConfig": 'vehicles/etk800/etk854t_A.pc'}

# game settings for beamng
BEAMNG_GRAPHICS_SETTINGS = {'GraphicDisplayModes': 'Fullscreen',
                            'GraphicDisplayResolutions': '3840 1080'}

# relative pos of camera in car
BEAMNG_CAMERA_POS = (-0.3230, 0.1408, 0.9500)

# name of the beamng scenario map
BEAMNG_SCENARIO_MAP = 'italy'

# name of setpoint
BEAMNG_SCENARIO_SPAWNPOINT = 'small_village'

# extracted from italy.zip in contents: italy/main/MissionGroup/spawnpoints
# this is inelegant -- maybe look at beamngpy to see if spawnpoint keys can be passed directly
BEAMNG_SPAWNPOINTS = {'village_mountain':
                          {'pos': (262.389404, -891.666626, 246.920883), 'rot': (0.0, -0.0, -105.00001087694228)},
                      'airport':
                          {'pos': (-1045.27136, 1636.64014, 152.583511), 'rot': (0.0, -0.0, 169.25541714966164)},
                      'crossroads':
                          {'pos': (729.62677, 763.914001, 177.753006), 'rot': (0.0, -0.0, 25.49583757115014)},
                      'runway':
                          {'pos': (-1887.9967, 1585.78821, 152.583542), 'rot': (0.0, -0.0, -102.46925237646784)},
                      'port':
                          {'pos': (487.19574, 1593.43286, 139.207413), 'rot': (0.0, -0.0, 179.99999402358202)},
                      'city':
                          {'pos': (1176.81909, 1113.59192, 157.5), 'rot': (0.0, -0.0, 179.99999402358202)},
                      'town_east':
                          {'pos': (1114.92346, -689.113403, 146.186447), 'rot': (0.0, -0.0, -1.293279448751198)},
                      'small_village':
                          {'pos': (-690.403564, -1338.64136, 140.215942), 'rot': (0.0, -0.0, 85.01954390247003)},
                      'castle_town':
                          {'pos': (-969.635193, 953.628723, 392.483368), 'rot': (0.0, -0.0, 74.9999865878277)}}


class DemonstratorNetworkConfig:
    """data class to store demonstrator network configuration"""

    @classmethod
    def from_setup_env(cls, fname: str):
        """create instance from Besspin target setupEnv.json"""
        import json, os, re
        print(f"Loading config from {fname}")
        assert os.path.exists(fname)
        with open(fname, "r") as f:
            senv = json.load(f)
            assert "setupCyberPhys" in senv
            csenv = senv["setupCyberPhys"]
            csenv = {d["name"]: d["val"] for d in csenv}

            # extract network ports and organize into a dict
            network_ports = {"cyberphysNetworkPorts": {}}
            for se in senv["setupEnv"]:
                match = re.match("cyberPhys(.*)Port", se["name"])
                if match:
                    pname = match.group(1)[0].lower() + match.group(1)[1:] + "Port"
                    network_ports["cyberphysNetworkPorts"][pname] = int(se["val"])

        return cls(**{**csenv, **network_ports})
    
    def getCmdNetworkNodes(self, component_name: str) -> (str, [str]):
        "Return a tuple (host_ip, [subcribers_ip])"
        nodes = self.nodes
        cmdport = self.port_network_commandPort
        host = nodes[component_name]
        subscribers = [ f"{node}:{cmdport}" for node in nodes.values() if node != host]
        host = f"{host}:{cmdport}"
        print(f"host: {host}, subscribers: {subscribers}")
        return host, subscribers

    def __init__(self,
                 cyberPhysWhitelists = None,
                 cyberPhysBlacklists = None,
                 cyberPhysNodes = None,
                 cyberPhysComponentPorts = None,
                 cyberphysNetworkPorts = None,
                 cyberPhysComponentBaseTopic = None,
                 cyberPhysWatchdogFrequency = 2):

        self.whitelists = cyberPhysWhitelists if cyberPhysWhitelists else {}
        self.blacklists = cyberPhysBlacklists if cyberPhysBlacklists else {}
        self.nodes = cyberPhysNodes if cyberPhysNodes else {}
        self.component_ports = cyberPhysComponentPorts if cyberPhysComponentPorts else {}
        self.network_ports = cyberphysNetworkPorts if cyberphysNetworkPorts else {}
        self.base_topic = cyberPhysComponentBaseTopic if cyberPhysComponentBaseTopic else {}
        self.watchdog_frequency = cyberPhysWatchdogFrequency

        # create dynamic attributes for flat access (prefix with category)
        # danger...
        self.__dict__.update({f"ip_{k}": v for k, v in self.nodes.items()})
        self.__dict__.update({f"wl_{k}": v for k, v in self.whitelists.items()})
        self.__dict__.update({f"bl_{k}": v for k, v in self.blacklists.items()})
        self.__dict__.update({f"port_component_{k}": v for k, v in self.component_ports.items()})
        self.__dict__.update({f"port_network_{k}": v for k, v in self.network_ports.items()})
