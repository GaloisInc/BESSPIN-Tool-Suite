"""Cyberphys CAN Frames Specification
Project: SSITH CyberPhysical Demonstrator
Name: python/canspecs.py
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Michal Podhradsky <mpodhradsky@galois.com>
Date: 17 March 2021
This file was created by SSITH-FETT-Target/build/cyberphys/canlib/make_can_spec.py
Version hash: f50e0a68352312d07b0ce23fc3a46a33
"""

# Name: gear
# Units: N/A
# Type: uint8_t
# Description: selected gear
CAN_ID_GEAR: int = 0XAAF01000

# Name: throttle_input
# Units: %
# Type: uint8_t
# Description: Throttle input state
CAN_ID_THROTTLE_INPUT: int = 0XAAF01A00

# Name: brake_input
# Units: %
# Type: uint8_t
# Description: Brake input state
CAN_ID_BRAKE_INPUT: int = 0XAAF01B00

# Name: steering_input
# Units: N/A
# Type: int8_t
# Description: Steering input state
CAN_ID_STEERING_INPUT: int = 0XAAF01D00

# Name: fuel
# Units: %
# Type: uint8_t
# Description: Percentage of fuel remaining
CAN_ID_FUEL: int = 0XAAFEAA00

# Name: car_x
# Units: m
# Type: float
# Description: infotainment position of car to display x coordinate
CAN_ID_CAR_X: int = 0XAAFEAAC1

# Name: car_y
# Units: m
# Type: float
# Description: infotainment position of car to display y coordinate
CAN_ID_CAR_Y: int = 0XAAFEADF6

# Name: car_z
# Units: m
# Type: float
# Description: infotainment position of car to display z coordinate
CAN_ID_CAR_Z: int = 0XAAFEAABF

# Name: car_r
# Units: m
# Type: float
# Description: infotainment position of car to display r rotation
CAN_ID_CAR_R: int = 0XAACDAD11

# Name: button_pressed
# Units: N/A
# Type: uint8_t
# Description: Button pressed on infotainment screen.0x01 Station 1 0x02 Station 2 0x03 station 3  0x10 volume down  0x11 volume up
CAN_ID_BUTTON_PRESSED: int = 0XAAFECA00

# Name: music_state
# Units: N/A
# Type: uint8_t
# Description: Bit 0 music pause/play bit 1-2: music station  bit 3-7 volume
CAN_ID_MUSIC_STATE: int = 0XAA2FEEF2

# Name: heartbeat_req
# Units: N/A
# Type: uint32_t
# Description: Heartbeat request with request number in network byte order
CAN_ID_HEARTBEAT_REQ: int = 0XAABEA737

# Name: heartbeat_ack
# Units: N/A
# Type: [uint32_t]
# Description: First 4 bytes are the sender ID (sender IP address) | Heartbeat acknowledgment with number matching a heartbeat_req in network byte order
CAN_ID_HEARTBEAT_ACK: int = 0XAABEA225

# Name: component_ready
# Units: N/A
# Type: uint32_t
# Description: Component ID (Sender IP)
CAN_ID_COMPONENT_READY: int = 0XAAFECB00

# Name: component_error
# Units: N/A
# Type: [uint32_t]
# Description: Component ID (Sender IP) | Error type
CAN_ID_COMPONENT_ERROR: int = 0XAAFECC00

