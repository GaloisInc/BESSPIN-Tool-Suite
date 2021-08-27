/*
* Cyberphys Cyberphys Component IDs
* Project: SSITH CyberPhysical Demonstrator
* Name: lib/componentids.h
* Author: Steven Osborn <steven@lolsborn.com>, Kristofer Dobelstein, Ethan Lew <elew@galois.com>
* Michal Podhradsky <mpodhradsky@galois.com>
* Date: 27 August 2021
* This file was created by BESSPIN-Tool-Suite/besspin/cyberPhys/canlib/make_can_spec.py
*/

#ifndef COMPONENT_IDS_H
#define COMPONENT_IDS_H
#define SCENARIO_BASELINE 0x11
#define SCENARIO_SECURE_INFOTAINMENT 0x12
#define SCENARIO_SECURE_ECU 0x13
#define FUNCTIONALITY_NONE 0x15
#define FUNCTIONALITY_MINIMAL 0x16
#define FUNCTIONALITY_MEDIUM 0x17
#define FUNCTIONALITY_FULL 0x18
#define BESSPIN_TOOL_FREERTOS 0x20
#define FREERTOS_1 0x21
#define FREERTOS_2_CHERI 0x22
#define FREERTOS_3 0x23
#define DEBIAN_1 0x24
#define DEBIAN_2_LMCO 0x25
#define DEBIAN_3 0x26
#define TEENSY 0x27
#define BESSPIN_TOOL_DEBIAN 0x28
#define IGNITION 0x30
#define LED_COMPONENT 0x31
#define CAN_DISPLAY 0x32
#define HACKER_KIOSK 0x40
#define HACK_NONE 0x50
#define HACK_OTA 0x51
#define HACK_BRAKE 0x51
#define HACK_THROTTLE 0x52
#define HACK_TRANSMISSION 0x53
#define HACK_LKAS 0x54
#define HACK_INFOTAINMENT_VOLUME 0x55
#define HACK_INFOTAINMENT_MUSIC 0x56
#define INFOTAINMENT_THIN_CLIENT 0x60
#define INFOTAINMENT_SERVER_1 0x61
#define INFOTAINMENT_SERVER_2 0x62
#define INFOTAINMENT_SERVER_3 0x63
#define OTA_UPDATE_SERVER_1 0x64
#define OTA_UPDATE_SERVER_2 0x65
#define OTA_UPDATE_SERVER_3 0x66
#define BUTTON_STATION_1 0x01
#define BUTTON_STATION_2 0x02
#define BUTTON_STATION_3 0x03
#define BUTTON_VOLUME_DOWN 0x10
#define BUTTON_VOLUME_UP 0x11
#define SENSOR_THROTTLE 0xBE
#define SENSOR_BRAKE 0xBF
#define ERROR_UNSPECIFIED 0xF0
#define ERROR_NONE 0xFF

#endif
