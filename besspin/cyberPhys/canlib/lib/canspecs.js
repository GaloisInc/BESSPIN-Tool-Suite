/*
    * Cyberphys CAN Frames Specification
    * Project: SSITH CyberPhysical Demonstrator
    * Name: lib/canspecs.js
    * Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
    * Michal Podhradsky <mpodhradsky@galois.com>
    * Date: 03 June 2021
    * This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
    */

// Name: gear
// Units: N/A
// Type: uint8_t
// Description: selected gear
const CAN_ID_GEAR = 0XAAF01000
const CAN_FORMAT_GEAR = "!B"

// Name: throttle_input
// Units: %
// Type: uint8_t
// Description: Throttle input state
const CAN_ID_THROTTLE_INPUT = 0XAAF01A00
const CAN_FORMAT_THROTTLE_INPUT = "!B"

// Name: brake_input
// Units: %
// Type: uint8_t
// Description: Brake input state
const CAN_ID_BRAKE_INPUT = 0XAAF01B00
const CAN_FORMAT_BRAKE_INPUT = "!B"

// Name: steering_input
// Units: N/A
// Type: int8_t
// Description: Steering input state
const CAN_ID_STEERING_INPUT = 0XAAF01D00
const CAN_FORMAT_STEERING_INPUT = "!b"

// Name: fuel
// Units: %
// Type: uint8_t
// Description: Percentage of fuel remaining
const CAN_ID_FUEL = 0XAAFEAA00
const CAN_FORMAT_FUEL = "!B"

// Name: car_x
// Units: m
// Type: float
// Description: infotainment position of car to display x coordinate
const CAN_ID_CAR_X = 0XAAFEAAC1
const CAN_FORMAT_CAR_X = "!f"

// Name: car_y
// Units: m
// Type: float
// Description: infotainment position of car to display y coordinate
const CAN_ID_CAR_Y = 0XAAFEADF6
const CAN_FORMAT_CAR_Y = "!f"

// Name: car_z
// Units: m
// Type: float
// Description: infotainment position of car to display z coordinate
const CAN_ID_CAR_Z = 0XAAFEAABF
const CAN_FORMAT_CAR_Z = "!f"

// Name: car_r
// Units: m
// Type: float
// Description: infotainment position of car to display r rotation
const CAN_ID_CAR_R = 0XAACDAD11
const CAN_FORMAT_CAR_R = "!f"

// Name: button_pressed
// Units: N/A
// Type: uint8_t
// Description: Button pressed on infotainment screen.0x01 Station 1 0x02 Station 2 0x03 station 3  0x10 volume down  0x11 volume up
const CAN_ID_BUTTON_PRESSED = 0XAAFECA00
const CAN_FORMAT_BUTTON_PRESSED = "!B"

// Name: infotainment_state
// Units: N/A
// Type: uint8_t
// Description: Bit 0 music pause/play bit 1-2: music station  bit 3-7 volume
const CAN_ID_INFOTAINMENT_STATE = 0XAA2FEEF2
const CAN_FORMAT_INFOTAINMENT_STATE = "!B"

// Name: heartbeat_req
// Units: N/A
// Type: uint32_t
// Description: Heartbeat request number (uint32_t)
const CAN_ID_HEARTBEAT_REQ = 0XAABEA737
const CAN_FORMAT_HEARTBEAT_REQ = "!I"

// Name: heartbeat_ack
// Units: N/A
// Type: uint32_t | uint32_t
// Description: Component ID / sender IP address (uint32_t) | heartbeat request number (uint32_t)
const CAN_ID_HEARTBEAT_ACK = 0XAABEA225
const CAN_FORMAT_HEARTBEAT_ACK = "!II"

// Name: cmd_component_ready
// Units: N/A
// Type: uint32_t
// Description: Component ID / sender IP address (uint32_t)
const CAN_ID_CMD_COMPONENT_READY = 0XAAFEEB00
const CAN_FORMAT_CMD_COMPONENT_READY = "!I"

// Name: cmd_component_error
// Units: N/A
// Type: uint32_t | uint32_t
// Description: Component ID / sender IP address (uint32_t) | Error type (uint32_t)
const CAN_ID_CMD_COMPONENT_ERROR = 0XAAFEEB01
const CAN_FORMAT_CMD_COMPONENT_ERROR = "!II"

// Name: cmd_active_scenario
// Units: N/A
// Type: uint8_t
// Description: Scenario ID (uint8_t)
const CAN_ID_CMD_ACTIVE_SCENARIO = 0XAAFEEB02
const CAN_FORMAT_CMD_ACTIVE_SCENARIO = "!B"

// Name: cmd_hack_active
// Units: N/A
// Type: uint8_t
// Description: Hack ID (uint8_t)
const CAN_ID_CMD_HACK_ACTIVE = 0XAAFEEB03
const CAN_FORMAT_CMD_HACK_ACTIVE = "!B"

// Name: cmd_set_driving_mode
// Units: N/A
// Type: uint8_t
// Description:  Driving Mode Index (uint8_t)
const CAN_ID_CMD_SET_DRIVING_MODE = 0XAAFEEB07
const CAN_FORMAT_CMD_SET_DRIVING_MODE = "!B"

// Name: cmd_restart
// Units: N/A
// Type: uint32_t
// Description: Component ID / sender IP address (uint32_t)
const CAN_ID_CMD_RESTART = 0XAAFEEB04
const CAN_FORMAT_CMD_RESTART = "!I"

// Name: cmd_scenario_not_available
// Units: N/A
// Type: uint8_t
// Description: Scenario ID (uint8_t)
const CAN_ID_CMD_SCENARIO_NOT_AVAILABLE = 0XAAFEEB05
const CAN_FORMAT_CMD_SCENARIO_NOT_AVAILABLE = "!B"

// Name: cmd_scenario_available
// Units: N/A
// Type: uint8_t
// Description: Scenario ID (uint8_t)
const CAN_ID_CMD_SCENARIO_AVAILABLE = 0XAAFEEB06
const CAN_FORMAT_CMD_SCENARIO_AVAILABLE = "!B"

