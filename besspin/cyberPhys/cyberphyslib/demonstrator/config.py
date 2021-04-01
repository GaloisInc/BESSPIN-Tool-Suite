"""
Project: SSITH CyberPhysical Demonstrator
Name: config.py
Author: Steven Osborn <steven@lolsborn.com>, Ethan Lew <elew@galois.com>
Date: 01 January 2021

Cyberphys Demonstrator Configuration Variables
"""

CAN_PORT = 5002
INFO_UI_PORT = 5013

SIM_IP = "192.168.0.231" # Sim PC IP

RADIO_SOUND_DIR = r"C:\\sound"  # FIXME: commit songs to repo? (requires merge from infotainment-ui branch)

# See cyberPhys-test.ini for IP allocation
# Also see https://github.com/GaloisInc/SSITH-CyberPhys/issues/225
BASE_WHITELIST = ["10.88.88.11", "10.88.88.12"] # Scenario 1: Baseline ECU + Baseline Infotainment
SSITH_INFO_WHITELIST = ["10.88.88.21", "10.88.88.22"] # Scenario 2: Baseline ECU + Secure Infotainment
SSITH_ECU_WHITELIST = ["10.88.88.31", "10.88.88.32"] # Scenario 3: Secure ECU + Baseline Infotainment

SSITH_INFO_BLACKLIST = False
SSITH_ECU_BLACKLIST = False
BASE_BLACKLIST = False

LOCATION_POLL_HZ = 10

BEAMNG_SETTINGS_PATH_RELATIVE = r"\BeamNG.drive\settings\\"

BEAMNG_GAME_INI_FILE_NAME = r"game-settings.ini"
BEAMNG_GAME_CS_FILE_NAME = r"game-settings.cs"

BEAMNG_CYBERPHYS_INI_FILE_NAME = r"game-settings_cyberphys.ini"
BEAMNG_CYBERPHYS_CS_FILE_NAME = r"game-settings_cyberphys.cs"

BEAMNG_PORT=64256
BEAMNG_PATH=r"C:\BeamNG.research"
# Override this if you need to change your user path. User path with spaces are not supported.
BEAMNG_USER_PATH=None
BEAMNG_OUTGAUGE_PORT = 4445 # Outgauge emulation

BEAMNG_COMPONENT_ELECTRIC = (5006, 'sensor-electric')
BEAMNG_COMPONENT_GFORCE   = (5006, 'sensor-gforce')
BEAMNG_COMPONENT_EVENTS   = (5006, 'beamng-events')
BEAMNG_COMPONENT_STATE    = (5006, 'beamng-state')
BEAMNG_COMPONENT_VEHICLE  = (5006, 'beamng-vehicle')
BEAMNG_COMPONENT_SENSORS  = (5006, "beamng-sensors")

# BeamNG service communication info
BEAMNG_COMPONENT_OUTPUT = [BEAMNG_COMPONENT_ELECTRIC,
                           BEAMNG_COMPONENT_GFORCE,
                           BEAMNG_COMPONENT_EVENTS,
                           BEAMNG_COMPONENT_STATE,
                           BEAMNG_COMPONENT_VEHICLE,
                           BEAMNG_COMPONENT_SENSORS
                          ]

BEAMNG_COMPONENT_INPUT = [(5005, 'beamng-commands')]

# keyword arguments to pass to Vehicle when creating a vehicle for the sim scenario
BEAMNG_VEHICLE_CONFIG = {"model" : "etk800", "partConfig": 'vehicles/etk800/etk854t_A.pc'}

# name of setpoint
BEAMNG_SCENARIO_SPAWNPOINT = 'small_village'

# extracted from italy.zip in contents: italy/main/MissionGroup/spawnpoints
# this is inelegant -- maybe look at beamngpy to see if spawnpoint keys can be passed directly
BEAMNG_ITALY_SPAWNPOINTS = {'village_mountain':
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


# LED Management Configuration
LED_MANAGEMENT_INPUT = [(5007, "pattern-request")]
