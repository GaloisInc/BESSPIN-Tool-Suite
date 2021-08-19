/**
 * Infotainment Server Types and Constants
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

#ifndef __INFOTAINMENT_DEFS__
#define __INFOTAINMENT_DEFS__

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

// we listen for CAN packets on the receive port
#define RECEIVE_PORT 5002

// we send CAN packets to the send port
#define SEND_PORT 5002

// the minimum volume
#define MIN_VOLUME 0

// the maximum volume
#define MAX_VOLUME 15

// the "default" volume
#define DEFAULT_VOLUME 8

// the default broadcast address (as a string)
#define DEFAULT_BROADCAST_ADDRESS "255.255.255.255"

// the states of the state machines; note that the current volume and
// selected station are not reflected here but are stored in variables.
// also note that ensuring distinct values requires these definitions to
// be coupled together, so the ordering of these declarations matters.

typedef enum { VOLUME_OFF,
               VOLUME_UNKNOWN,
               VOLUME_IN_RANGE,
               VOLUME_MAX } volume_state;
typedef enum { MUSIC_UNKNOWN = VOLUME_MAX + 1,
               MUSIC_PAUSED,
               MUSIC_PLAYING } music_state;
typedef enum { STATION_UNKNOWN = MUSIC_PLAYING + 1,
               STATION_SET } station_state;
// note: if the position doesn't need to be relayed, we can get rid of
// this part of the state machine and state storage and just deal with
// music state
typedef enum { POSITION_UNKNOWN = STATION_SET + 1,
               POSITION_SET } position_state;
typedef enum { START = POSITION_SET + 1,
               RUNNING,
               STOP } top_level_state;

typedef struct infotainment_state_t {
    top_level_state T;
    volume_state V;
    uint8_t volume;
    music_state M;
    station_state S;
    uint8_t station;
    position_state P;
    float pos_x;
    float pos_y;
    float pos_z;
    float pos_r;
} infotainment_state;

// constants for interpreting CAN messages; these are subject to 
// change until the CAN message spec is finalized

#define BUTTON_STATION_1 0x01
#define BUTTON_STATION_2 0x02
#define BUTTON_STATION_3 0x03
#define BUTTON_VOLUME_DOWN 0x10
#define BUTTON_VOLUME_UP 0x11

#define PAUSE_PLAY_MASK 1 // 0b1
#define STATION_MASK 6 // 0b110
#define VOLUME_MASK 248 // 0b11111000

// music state decode functions (takes the payload of a music state CAN packet)
#define play(c) (c & PAUSE_PLAY_MASK)
#define station(c) ((c & STATION_MASK) >> 1)
#define volume(c) ((c & VOLUME_MASK) >> 3)

// music state construction function (takes an infotainment_state_t)
#define music_state_packet(s) ((s.volume << 3) | (s.station << 1) | (1 & (s.M == MUSIC_PLAYING)))
// no need for bitmasks with the positions because they're just floats

#endif // __INFOTAINMENT_DEFS_H__
