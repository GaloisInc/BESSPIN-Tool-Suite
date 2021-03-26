/*
* Cyberphys CAN Frames Specification
* Project: SSITH CyberPhysical Demonstrator
* Name: python/canspecs.py
* Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
* Michal Podhradsky <mpodhradsky@galois.com>
* Date: 26 March 2021
* This file was created by SSITH-FETT-Target/build/cyberphys/canlib/make_can_spec.py
* Version hash: f50e0a68352312d07b0ce23fc3a46a33
*/

#ifndef CANSPECS_H
#define CANSPECS_H

// gear
// Type: uint8_t
// Sender: ECU
// Receiver: Ignition
// Bounds/Range: P, R, N, D
// Units: N/A
// J1939 compatible: YES
//
// selected gear
#define CAN_ID_GEAR 0XAAF01000
#define BYTE_LENGTH_GEAR 1
#define PGN_GEAR 122890

// throttle_input
// Type: uint8_t
// Sender: ECU
// Receiver: Ignition
// Bounds/Range: 0/100
// Units: %
// J1939 compatible: YES
//
// Throttle input state
#define CAN_ID_THROTTLE_INPUT 0XAAF01A00
#define BYTE_LENGTH_THROTTLE_INPUT 1
#define PGN_THROTTLE_INPUT 122932

// brake_input
// Type: uint8_t
// Sender: ECU
// Receiver: Ignition
// Bounds/Range: 0/100
// Units: %
// J1939 compatible: YES
//
// Brake input state
#define CAN_ID_BRAKE_INPUT 0XAAF01B00
#define BYTE_LENGTH_BRAKE_INPUT 1
#define PGN_BRAKE_INPUT 122934

// steering_input
// Type: int8_t
// Sender: ECU
// Receiver: Ignition
// Bounds/Range: -100..100
// Units: N/A
// J1939 compatible: YES
//
// Steering input state
#define CAN_ID_STEERING_INPUT 0XAAF01D00
#define BYTE_LENGTH_STEERING_INPUT 1
#define PGN_STEERING_INPUT 122938

// fuel
// Type: uint8_t
// Sender: Ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: 0/100
// Units: %
// J1939 compatible: YES
//
// Percentage of fuel remaining
#define CAN_ID_FUEL 0XAAFEAA00
#define BYTE_LENGTH_FUEL 1
#define PGN_FUEL 130552

// car_x
// Type: float
// Sender: Ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// Units: m
// J1939 compatible: No
//
// infotainment position of car to display x coordinate
#define CAN_ID_CAR_X 0XAAFEAAC1
#define BYTE_LENGTH_CAR_X 4

// car_y
// Type: float
// Sender: Ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// Units: m
// J1939 compatible: No
//
// infotainment position of car to display y coordinate
#define CAN_ID_CAR_Y 0XAAFEADF6
#define BYTE_LENGTH_CAR_Y 4

// car_z
// Type: float
// Sender: Ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// Units: m
// J1939 compatible: No
//
// infotainment position of car to display z coordinate
#define CAN_ID_CAR_Z 0XAAFEAABF
#define BYTE_LENGTH_CAR_Z 4

// car_r
// Type: float
// Sender: Ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// Units: m
// J1939 compatible: no
//
// infotainment position of car to display r rotation
#define CAN_ID_CAR_R 0XAACDAD11
#define BYTE_LENGTH_CAR_R 4

// button_pressed
// Type: uint8_t
// Sender: Infotainment Thin Client
// Receiver: Infotainment Server
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Button pressed on infotainment screen.0x01 Station 1 0x02 Station 2 0x03 station 3  0x10 volume down  0x11 volume up
#define CAN_ID_BUTTON_PRESSED 0XAAFECA00
#define BYTE_LENGTH_BUTTON_PRESSED 1

// infotainment_state
// Type: uint8_t
// Sender: Infotainment Server
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Bit 0 music pause/play bit 1-2: music station  bit 3-7 volume
#define CAN_ID_INFOTAINMENT_STATE 0XAA2FEEF2
#define BYTE_LENGTH_INFOTAINMENT_STATE 1

// heartbeat_req
// Type: uint32_t
// Sender: FETT Tool
// Receiver: All
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Heartbeat request number (uint32_t)
#define CAN_ID_HEARTBEAT_REQ 0XAABEA737
#define BYTE_LENGTH_HEARTBEAT_REQ 4

// heartbeat_ack
// Type: [uint32_t]
// Sender: All
// Receiver: FETT Tool
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Component ID / sender IP address (uint32_t) | heartbeat request number (uint32_t)
#define CAN_ID_HEARTBEAT_ACK 0XAABEA225
#define BYTE_LENGTH_HEARTBEAT_ACK 8

// cmd_component_ready
// Type: uint32_t
// Sender: All
// Receiver: All
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Component ID / sender IP address (uint32_t)
#define CAN_ID_CMD_COMPONENT_READY 0XAAFEEB00
#define BYTE_LENGTH_CMD_COMPONENT_READY 4

// cmd_component_error
// Type: [uint32_t]
// Sender: All
// Receiver: All
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Component ID / sender IP address (uint32_t) | Error type (uint32_t)
#define CAN_ID_CMD_COMPONENT_ERROR 0XAAFEEB01
#define BYTE_LENGTH_CMD_COMPONENT_ERROR 8

// cmd_active_scenario
// Type: uint8_t
// Sender: Hacker kiosk
// Receiver: Ignition
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Scenario ID (uint8_t)
#define CAN_ID_CMD_ACTIVE_SCENARIO 0XAAFEEB02
#define BYTE_LENGTH_CMD_ACTIVE_SCENARIO 1

// cmd_hack_active
// Type: uint8_t
// Sender: Hacker kiosk
// Receiver: Ignition
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Hack ID (uint8_t)
#define CAN_ID_CMD_HACK_ACTIVE 0XAAFEEB03
#define BYTE_LENGTH_CMD_HACK_ACTIVE 1

// cmd_restart
// Type: uint32_t
// Sender: Hacker kiosk
// Receiver: All
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Component ID / sender IP address (uint32_t)
#define CAN_ID_CMD_RESTART 0XAAFEEB04
#define BYTE_LENGTH_CMD_RESTART 4

// cmd_scenario_not_available
// Type: uint8_t
// Sender: FETT Tool
// Receiver: Hacker kiosk
// Bounds/Range: N/A
// Units: N/A
// J1939 compatible: No
//
// Scenario ID (uint8_t)
#define CAN_ID_CMD_SCENARIO_NOT_AVAILABLE 0XAAFEEB05
#define BYTE_LENGTH_CMD_SCENARIO_NOT_AVAILABLE 1

#endif
