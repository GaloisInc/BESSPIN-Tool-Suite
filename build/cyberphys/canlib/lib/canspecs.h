/*
* Cyberphys CAN Frames Specification
* Project: SSITH CyberPhysical Demonstrator
* Name: python/canspecs.py
* Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
* Michal Podhradsky <mpodhradsky@galois.com>
* Date: 05 March 2021
* This file was created by SSITH-FETT-Target/build/cyberphys/canlib/make_can_spec.py
* Version hash: f50e0a68352312d07b0ce23fc3a46a33
*/

#ifndef CANSPECS_H
#define CANSPECS_H

// gear (uint8_t)
// Sender: ECU
// Receiver: ignition
// Bounds/Range: P, R, N, D
// J1939 compatible: YES
// Description: 
//	selected gear
#define CAN_ID_GEAR 0XAAF01000
#define BYTE_LENGTH_GEAR 1
#define PGN_GEAR 122890

// throttle_input (uint8_t)
// Sender: ECU
// Receiver: ignition
// Bounds/Range: 0/100
// J1939 compatible: YES
// Description: 
//	Throttle input state
#define CAN_ID_THROTTLE_INPUT 0XAAF01A00
#define BYTE_LENGTH_THROTTLE_INPUT 1
#define PGN_THROTTLE_INPUT 122932

// brake_input (uint8_t)
// Sender: ECU
// Receiver: ignition
// Bounds/Range: 0/100
// J1939 compatible: YES
// Description: 
//	Brake input state
#define CAN_ID_BRAKE_INPUT 0XAAF01B00
#define BYTE_LENGTH_BRAKE_INPUT 1
#define PGN_BRAKE_INPUT 122934

// steering_input (int8_t)
// Sender: ECU
// Receiver: ignition
// Bounds/Range: -100..100
// J1939 compatible: YES
// Description: 
//	Steering input state
#define CAN_ID_STEERING_INPUT 0XAAF01D00
#define BYTE_LENGTH_STEERING_INPUT 1
#define PGN_STEERING_INPUT 122938

// fuel (uint8_t)
// Sender: ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: 0/100
// Units: %
// J1939 compatible: YES
// Description: 
//	Percentage of fuel remaining
#define CAN_ID_FUEL 0XAAFEAA00
#define BYTE_LENGTH_FUEL 1
#define PGN_FUEL 130552

// car_x (float)
// Sender: ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// Units: m
// J1939 compatible: No
// Description: 
//	infotainment position of car to display x coordinate
#define CAN_ID_CAR_X 0XAAFEAAC1
#define BYTE_LENGTH_CAR_X 4

// car_y (float)
// Sender: ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// Units: m
// J1939 compatible: No
// Description: 
//	infotainment position of car to display y coordinate
#define CAN_ID_CAR_Y 0XAAFEADF6
#define BYTE_LENGTH_CAR_Y 4

// car_z (float)
// Sender: ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// Units: m
// J1939 compatible: No
// Description: 
//	infotainment position of car to display z coordinate
#define CAN_ID_CAR_Z 0XAAFEAABF
#define BYTE_LENGTH_CAR_Z 4

// car_r (float)
// Sender: ignition
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// Units: m
// J1939 compatible: no
// Description: 
//	infotainment position of car to display r rotation
#define CAN_ID_CAR_R 0XAACDAD11
#define BYTE_LENGTH_CAR_R 4

// button_pressed (uint8_t)
// Sender: Infotainment Thin Client
// Receiver: Infotainment Server
// Bounds/Range: N/A
// J1939 compatible: No
// Description: 
//	Button pressed on infotainment screen.0x01 Station 1 0x02 Station 2 0x03 station 3  0x10 volume down  0x11 volume up
#define CAN_ID_BUTTON_PRESSED 0XAAFECA00
#define BYTE_LENGTH_BUTTON_PRESSED 1

// music_state (uint8_t)
// Sender: Infotainment Server
// Receiver: Infotainment Thin Client
// Bounds/Range: N/A
// J1939 compatible: No
// Description: 
//	Bit 0 music pause/play bit 1-2: music station  bit 3-7 volume
#define CAN_ID_MUSIC_STATE 0XAA2FEEF2
#define BYTE_LENGTH_MUSIC_STATE 1

// heartbeat_req (uint32_t)
// Sender: Admin PC
// Receiver: All
// Bounds/Range: N/A
// J1939 compatible: No
// Description: 
//	Heartbeat request with request number in network byte order
#define CAN_ID_HEARTBEAT_REQ 0XAABEA737
#define BYTE_LENGTH_HEARTBEAT_REQ 4

// heartbeat_ack (uint32_t)
// Sender: All
// Receiver: Admin PC
// Bounds/Range: N/A
// J1939 compatible: No
// Description: 
//	First 4 bytes are the sender ID (sender IP address) | Heartbeat acknowledgment with number matching a heartbeat_req in network byte order
#define CAN_ID_HEARTBEAT_ACK 0XAABEA225
#define BYTE_LENGTH_HEARTBEAT_ACK 8

// no_operation (uint8_t)
// Sender: Infotainment Server
// Receiver: Infotainment Server
// Bounds/Range: N/A
// J1939 compatible: No
// Description: 
//	CAN message used to detect the infotainment server local IP address
#define CAN_ID_NO_OPERATION 0XAA47ADD7
#define BYTE_LENGTH_NO_OPERATION 1

#endif
