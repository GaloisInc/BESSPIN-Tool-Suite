"""Cyberphys CAN Frames Specification
Project: SSITH CyberPhysical Demonstrator
Name: ../cyberphyslib/cyberphyslib/canlib/canspecs.py
Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
Michal Podhradsky <mpodhradsky@galois.com>
Date: 24 August 2021
This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
"""

# Name: gear
# Units: N/A
# Type: uint8_t
# Description: selected gear
CAN_ID_GEAR: int = 0XAAF01000
CAN_FORMAT_GEAR: str = "!B"
CAN_DLC_GEAR: int = 1

# Name: throttle_input
# Units: %
# Type: uint8_t
# Description: Throttle input state
CAN_ID_THROTTLE_INPUT: int = 0XAAF01A00
CAN_FORMAT_THROTTLE_INPUT: str = "!B"
CAN_DLC_THROTTLE_INPUT: int = 1

# Name: brake_input
# Units: %
# Type: uint8_t
# Description: Brake input state
CAN_ID_BRAKE_INPUT: int = 0XAAF01B00
CAN_FORMAT_BRAKE_INPUT: str = "!B"
CAN_DLC_BRAKE_INPUT: int = 1

# Name: steering_input
# Units: N/A
# Type: int8_t
# Description: Steering input state
CAN_ID_STEERING_INPUT: int = 0XAAF01D00
CAN_FORMAT_STEERING_INPUT: str = "!b"
CAN_DLC_STEERING_INPUT: int = 1

# Name: fuel
# Units: %
# Type: uint8_t
# Description: Percentage of fuel remaining
CAN_ID_FUEL: int = 0XAAFEAA00
CAN_FORMAT_FUEL: str = "!B"
CAN_DLC_FUEL: int = 1

# Name: car_x
# Units: m
# Type: float
# Description: infotainment position of car to display x coordinate
CAN_ID_CAR_X: int = 0XAAFEAAC1
CAN_FORMAT_CAR_X: str = "!f"
CAN_DLC_CAR_X: int = 4

# Name: car_y
# Units: m
# Type: float
# Description: infotainment position of car to display y coordinate
CAN_ID_CAR_Y: int = 0XAAFEADF6
CAN_FORMAT_CAR_Y: str = "!f"
CAN_DLC_CAR_Y: int = 4

# Name: car_z
# Units: m
# Type: float
# Description: infotainment position of car to display z coordinate
CAN_ID_CAR_Z: int = 0XAAFEAABF
CAN_FORMAT_CAR_Z: str = "!f"
CAN_DLC_CAR_Z: int = 4

# Name: car_r
# Units: m
# Type: float
# Description: infotainment position of car to display r rotation
CAN_ID_CAR_R: int = 0XAACDAD11
CAN_FORMAT_CAR_R: str = "!f"
CAN_DLC_CAR_R: int = 4

# Name: button_pressed
# Units: N/A
# Type: uint8_t
# Description: Button pressed on infotainment screen.0x01 Station 1 0x02 Station 2 0x03 station 3  0x10 volume down  0x11 volume up
CAN_ID_BUTTON_PRESSED: int = 0XAAFECA00
CAN_FORMAT_BUTTON_PRESSED: str = "!B"
CAN_DLC_BUTTON_PRESSED: int = 1

# Name: infotainment_state
# Units: N/A
# Type: uint8_t
# Description: Bit 0 music pause/play bit 1-2: music station  bit 3-7 volume
CAN_ID_INFOTAINMENT_STATE: int = 0XAA2FEEF2
CAN_FORMAT_INFOTAINMENT_STATE: str = "!B"
CAN_DLC_INFOTAINMENT_STATE: int = 1

# Name: heartbeat_req
# Units: N/A
# Type: uint32_t
# Description: Heartbeat request number (uint32_t)
CAN_ID_HEARTBEAT_REQ: int = 0XAABEA737
CAN_FORMAT_HEARTBEAT_REQ: str = "!I"
CAN_DLC_HEARTBEAT_REQ: int = 4

# Name: heartbeat_ack
# Units: N/A
# Type: uint32_t | uint32_t
# Description: Component ID / sender IP address (uint32_t) | heartbeat request number (uint32_t)
CAN_ID_HEARTBEAT_ACK: int = 0XAABEA225
CAN_FORMAT_HEARTBEAT_ACK: str = "!II"
CAN_DLC_HEARTBEAT_ACK: int = 8

# Name: cmd_component_ready
# Units: N/A
# Type: uint32_t
# Description: Component ID / sender IP address (uint32_t)
CAN_ID_CMD_COMPONENT_READY: int = 0XAAFEEB00
CAN_FORMAT_CMD_COMPONENT_READY: str = "!I"
CAN_DLC_CMD_COMPONENT_READY: int = 4

# Name: cmd_component_error
# Units: N/A
# Type: uint32_t | uint32_t
# Description: Component ID / sender IP address (uint32_t) | Error type (uint32_t)
CAN_ID_CMD_COMPONENT_ERROR: int = 0XAAFEEB01
CAN_FORMAT_CMD_COMPONENT_ERROR: str = "!II"
CAN_DLC_CMD_COMPONENT_ERROR: int = 8

# Name: cmd_active_scenario
# Units: N/A
# Type: uint8_t
# Description: Scenario ID (uint8_t)
CAN_ID_CMD_ACTIVE_SCENARIO: int = 0XAAFEEB02
CAN_FORMAT_CMD_ACTIVE_SCENARIO: str = "!B"
CAN_DLC_CMD_ACTIVE_SCENARIO: int = 1

# Name: cmd_hack_active
# Units: N/A
# Type: uint8_t
# Description: Hack ID (uint8_t)
CAN_ID_CMD_HACK_ACTIVE: int = 0XAAFEEB03
CAN_FORMAT_CMD_HACK_ACTIVE: str = "!B"
CAN_DLC_CMD_HACK_ACTIVE: int = 1

# Name: cmd_set_driving_mode
# Units: N/A
# Type: uint8_t
# Description:  Driving Mode Index (uint8_t)
CAN_ID_CMD_SET_DRIVING_MODE: int = 0XAAFEEB07
CAN_FORMAT_CMD_SET_DRIVING_MODE: str = "!B"
CAN_DLC_CMD_SET_DRIVING_MODE: int = 4

# Name: cmd_restart
# Units: N/A
# Type: uint32_t
# Description: Component ID / sender IP address (uint32_t)
CAN_ID_CMD_RESTART: int = 0XAAFEEB04
CAN_FORMAT_CMD_RESTART: str = "!I"
CAN_DLC_CMD_RESTART: int = 4

# Name: cmd_functionality_level
# Units: N/A
# Type: uint8_t
# Description: Functionality level (uint8_t)
CAN_ID_CMD_FUNCTIONALITY_LEVEL: int = 0XAAFEEB05
CAN_FORMAT_CMD_FUNCTIONALITY_LEVEL: str = "!B"
CAN_DLC_CMD_FUNCTIONALITY_LEVEL: int = 1

