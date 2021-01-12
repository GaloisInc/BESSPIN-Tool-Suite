/**
 * Infotainment Server
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

// general includes
#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h> 
#include <netinet/in.h>
#include <sys/types.h> 
#include <sys/socket.h> 

#include "can.h"
#include "canlib.h"

#include "infotainment_defs.h"
#include "infotainment_debug.h"
#include "infotainment_server.h"
#include "infotainment_utils.h"

// initialize global state variables
infotainment_state the_state = { .T = START };

bool initialize(void) {
    if (the_state.T == RUNNING) {
        error("initialize called on running server\n");
    }

    // initialize the state; we don't know much initially but
    // we'll set the various fields to sane values
    the_state.V = VOLUME_UNKNOWN;
    the_state.M = MUSIC_UNKNOWN;
    the_state.S = STATION_UNKNOWN;
    the_state.P = POSITION_UNKNOWN;
    the_state.volume = 0;
    the_state.station = 0;
    the_state.pos_x = 0.0f;
    the_state.pos_y = 0.0f;
    the_state.pos_z = 0.0f;
    the_state.T = RUNNING;

    return true;
}

int main_loop(void) {
    // initialize socket address and buffer data structures
    struct sockaddr_in broadcast_address;
    struct sockaddr_in receive_address;
    socklen_t receive_address_len;
    uint8_t message[MESSAGE_BUFFER_SIZE];
    can_frame *frame;

    debug("socket number is %d\n", udp_socket(CAN_NETWORK_PORT));
    
    while (the_state.T == RUNNING) {
        // zero out the buffer
        memset(&message, 0, MESSAGE_BUFFER_SIZE);

        // receive a packet
        frame = receive_frame(CAN_NETWORK_PORT, message, MESSAGE_BUFFER_SIZE, 
                              &receive_address, &receive_address_len);
        
        // attempt to decode the frame and see if it is for us
        if (frame == NULL) {
            continue;
        } else if (!is_relevant(frame->can_id)) {
            debug("received CAN message with irrelevant ID %x\n", frame->can_id);
            continue;
        }

        // change our state based on the received CAN frame

        debug("processing CAN message with ID %x\n", frame->can_id);
        bool position_updated = false;
        switch (frame->can_id) {
            case CAN_ID_CAR_X:
            case CAN_ID_CAR_Y:
            case CAN_ID_CAR_Z:
                position_updated = update_position(frame);
                break;
            
            case CAN_ID_BUTTON_PRESSED:
                handle_button_press(frame);
        }

        // broadcast the new state; we always broadcast the current music state, 
        // and we also broadcast any position state that has been updated

        broadcast_music_state();
        if (position_updated) {
            broadcast_updated_position(frame->can_id);
        }
    }

    debug("stop signal received, cleaning up\n");
    // close the UDP socket in an orderly fashion since we're
    // no longer listening
    close(udp_socket(CAN_NETWORK_PORT));

    return 0;
}

bool is_relevant(canid_t can_id) {
    bool result = false;

    switch (can_id) {
        case CAN_ID_BUTTON_PRESSED:
        case CAN_ID_CAR_X:
        case CAN_ID_CAR_Y:
        case CAN_ID_CAR_Z:
            result = true;
    }

    return result;
}

bool update_position(can_frame *frame) {
    // make sure the frame is an appropriate type
    assert(frame->can_id == CAN_ID_CAR_X || frame->can_id == CAN_ID_CAR_Y ||
           frame->can_id == CAN_ID_CAR_Z);

    // interpret the payload as a float
    float *position = (float *) frame->data;
    float *old_position = position_for_dimension(the_state, frame->can_id);    
    char dimension = char_for_dimension(frame->can_id);
    bool changed = false;

    if (*old_position == *position) {
        debug("%c-coordinate update (%f) results in no change\n", 
              dimension, *position);
    } else {
        *old_position = *position;
        changed = true;
        debug("updated %c-coordinate to %f\n", dimension, *old_position);
    }

    return changed;
}

bool handle_button_press(can_frame *frame) {
    // make sure the frame is an appropriate type
    assert(frame->can_id == CAN_ID_BUTTON_PRESSED);

    // interpret the payload as a single byte
    unsigned char *payload = (unsigned char *) frame->data;
    bool changed = false;

    switch (*payload) {
        case BUTTON_STATION_1:
            debug("station 1 set\n");
            changed = set_station(1);
            break;
        case BUTTON_STATION_2:
            debug("station 2 set\n");
            changed = set_station(2);
            break;
        case BUTTON_STATION_3:
            debug("station 3 set\n");
            changed = set_station(3);
            break;
        case BUTTON_VOLUME_DOWN:
            debug("volume down pressed\n");
            changed = decrease_volume();
            break;
        case BUTTON_VOLUME_UP:
            debug("volume up pressed\n");
            changed = increase_volume();
            break;
        default:
            debug("invalid button press (%d) received, ignoring\n", 
                  *payload);
    }

    return changed;
}

bool set_station(uint8_t station) {
    bool changed = !(the_state.station == station);
    the_state.M = MUSIC_PLAYING;
    the_state.S = STATION_SET;
    the_state.station = station;
    return changed;
}

bool increase_volume() {
    bool changed = false;
    switch (the_state.V) {
        case VOLUME_UNKNOWN:
            changed = true;
            the_state.V = VOLUME_IN_RANGE;
            the_state.volume = DEFAULT_VOLUME;
            break;
        case VOLUME_IN_RANGE:
        case VOLUME_OFF:
            changed = !(the_state.volume == MAX_VOLUME);
            the_state.volume = the_state.volume + 1;
            if (the_state.volume == MAX_VOLUME) {
                the_state.V = VOLUME_MAX;
            } else {
                the_state.V = VOLUME_IN_RANGE;
            }
            break;
        default:
            break;
    }
    return changed;
}

bool decrease_volume() {
    bool changed = false;
    switch (the_state.V) {
        case VOLUME_UNKNOWN:
            changed = true;
            the_state.V = VOLUME_IN_RANGE;
            the_state.volume = DEFAULT_VOLUME;
            break;
        case VOLUME_IN_RANGE:
        case VOLUME_MAX:
            changed = !(the_state.volume == MIN_VOLUME);
            the_state.volume = the_state.volume - 1;
            if (the_state.volume == MIN_VOLUME) {
                the_state.V = VOLUME_OFF;
            } else {
                the_state.V = VOLUME_IN_RANGE;
            }
            break;
        default:
            break;
    }
    return changed;
}

void broadcast_music_state() {
    if (the_state.M == MUSIC_UNKNOWN || the_state.S == STATION_UNKNOWN ||
        the_state.V == VOLUME_UNKNOWN) {
        debug("warning: broadcasting music state with default values\n");
    }

    uint8_t data = music_state_packet(the_state);
    can_frame frame = { .can_id = CAN_ID_MUSIC_STATE, 
                        .can_dlc = BYTE_LENGTH_MUSIC_STATE };
    frame.data[0] = data;

    debug("broadasting music state frame: music %d, station %d, volume %d\n",
          the_state.M == MUSIC_PLAYING, the_state.station, the_state.volume);
    broadcast_frame(CAN_NETWORK_PORT, MUX_PORT, &frame);
}

void broadcast_updated_position(canid_t can_id) {
    // make sure the ID is appropriate
    assert(can_id == CAN_ID_CAR_X || can_id == CAN_ID_CAR_Y ||
           can_id == CAN_ID_CAR_Z);

    float *position = position_for_dimension(the_state, can_id);
    char dimension = char_for_dimension(can_id);

    // BYTE_LENGTH_CAR_X is the same as Y and Z
    can_frame frame = { .can_id = can_id, .can_dlc = BYTE_LENGTH_CAR_X };
    float *buffer = (float *) frame.data;
    *buffer = *position;

    debug("broadcasting new %c position: %f\n", dimension, *position);
    broadcast_frame(CAN_NETWORK_PORT, MUX_PORT, &frame);
}

void stop(void) {
    debug("stopping state machine after current iteration\n");
    the_state.T = STOP;
}
