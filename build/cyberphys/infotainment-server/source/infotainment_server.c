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
#include "cyberphys.h"

#include "infotainment_defs.h"
#include "infotainment_debug.h"
#include "infotainment_server.h"

// initialize global state variables
infotainment_state the_state = { .T = START };

bool initialize(void) {
    if (the_state.T == RUNNING) {
        error("initialize called on running server");
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

int udp_socket(void) {
    static int socketfd = -1;
    static struct sockaddr_in listen_address;

    // create the socket if it doesn't exist or is closed     
    if (socketfd < 0 || (fcntl(socketfd, F_GETFD) == -1 && errno != EBADF)) {
        debug("creating socket\n");

        if ((socketfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
            error("unable to create socket: error %d\n", errno);
        } 
        
        // initialize the listen address
        memset((char *) &listen_address, 0, sizeof(listen_address));
        listen_address.sin_family = AF_INET;
        listen_address.sin_port = htons(CAN_NETWORK_PORT);
        listen_address.sin_addr.s_addr = htonl(INADDR_ANY);

        // bind the socket to the port
        if (bind(socketfd, 
                 (struct sockaddr *) &listen_address, 
                 sizeof(listen_address)) == -1) {
            error("unable to listen on CAN network port (%d)\n", 
                  CAN_NETWORK_PORT);
        }

        // set socket options to receive broadcasts
        int broadcast_permission = 1;
        if (setsockopt(socketfd, SOL_SOCKET, SO_BROADCAST, (void *) &broadcast_permission, 
                       sizeof(broadcast_permission)) < 0) {
            error("unable to set broadcast listening mode\n");
        }

        debug("socket created, listening for broadcasts on CAN network port (%d)\n", 
              CAN_NETWORK_PORT);
    }

    return socketfd;   
}

int main_loop(void) {
    // initialize socket address and buffer data structures
    struct sockaddr_in broadcast_address;
    struct sockaddr_in receive_address;
    socklen_t receive_address_len;
    uint8_t message[MESSAGE_BUFFER_SIZE];
    size_t message_len;
    can_frame *frame;

    // broadcast all outgoing packets to the world (but our world is small)
    broadcast_address.sin_family = AF_INET;
    broadcast_address.sin_port = htons(MUX_PORT);
    broadcast_address.sin_addr.s_addr = htonl(INADDR_BROADCAST);

    debug("socket number is %d\n", udp_socket());
    
    while (the_state.T == RUNNING) {
        // zero out the buffer
        memset(&message, 0, MESSAGE_BUFFER_SIZE);

        // receive a packet
        int32_t bytes_received = 
            canframe_recvfrom(udp_socket(), &message, MESSAGE_BUFFER_SIZE, 0, // no flags
                              &receive_address, &receive_address_len);

        // decode the packet
        if (bytes_received < 0) {
            debug("CAN message receive failed\n");
            continue;
        } else if (bytes_received == 0) {
            debug("Received empty CAN message\n");
            continue;
        }

        debug("received %i bytes\n", bytes_received);
        
        // attempt to decode the frame and see if it is for us
        frame = (can_frame *) &message[0];
        if (bytes_received <= sizeof(can_frame)) {
            // extract data field
            message_len = frame->can_dlc;
            if (message_len != bytes_received - 5) {
                debug("received CAN message with invalid length\n");
                continue;
            }
            // check for CAN ID that matches ours
            if (!is_relevant(frame->can_id)) {
                debug("received CAN message with irrelevant ID %x\n", frame->can_id);
                continue;
            }
        } else {
            debug("received J1939 message, ignoring\n");
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

        broadcast_music_state(&broadcast_address);
        if (position_updated) {
            broadcast_updated_position(&broadcast_address, frame->can_id);
        }
    }

    debug("stop signal received, cleaning up\n");
    // close the UDP socket in an orderly fashion since we're
    // no longer listening
    close(udp_socket());

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
    if (frame->can_id != CAN_ID_CAR_X && frame->can_id != CAN_ID_CAR_Y &&
        frame->can_id != CAN_ID_CAR_Z) {
        error("attempt to update position from invalid frame, this should never happen");
    }

    // interpret the payload as a float
    float *position;
    float *old_position;
    position = (float *) frame->data;
    
    bool changed = false;
    const char *dimension = "";
    switch (frame->can_id) {
        case CAN_ID_CAR_X:
            dimension = "x";
            old_position = &the_state.pos_x;
            break;
        case CAN_ID_CAR_Y:
            dimension = "y";
            old_position = &the_state.pos_y;
            break;
        case CAN_ID_CAR_Z:
            dimension = "z";
            old_position = &the_state.pos_z;
            break;
    }

    if (*old_position == *position) {
        debug("%s-coordinate update (%f) results in no change\n", dimension, *position);
    } else {
        *old_position = *position;
        changed = true;
        debug("updated %s-coordinate to %f\n", dimension, *old_position);
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
            debug("invalid button press (%d) received, ignoring\n", *payload);
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

void broadcast_music_state(struct sockaddr_in *broadcast_address) {
    if (the_state.M == MUSIC_UNKNOWN || the_state.S == STATION_UNKNOWN ||
        the_state.V == VOLUME_UNKNOWN) {
        debug("warning: broadcasting music state with default values\n");
    }

    uint8_t data = music_state_packet(the_state);
    can_frame frame = { .can_id = CAN_ID_INFOTAINMENT_STATE, .can_dlc = 1 };
    frame.data[0] = data;

    debug("broadasting music state frame: music %d, station %d, volume %d",
          the_state.M == MUSIC_PLAYING, the_state.station, the_state.volume);
    canframe_sendto(udp_socket(), &frame, sizeof(frame), 0, // no flags
                    broadcast_address, sizeof(broadcast_address));
}

void broadcast_updated_position(struct sockaddr_in *broadcast_address, 
                                canid_t can_id) {
    float position = 0.0f;
    char *dimension = "";
    switch (can_id) {
        case CAN_ID_CAR_X:
            position = the_state.pos_x;
            dimension = "x";
            break;
        case CAN_ID_CAR_Y:
            position = the_state.pos_y;
            dimension = "y";
            break;
        case CAN_ID_CAR_Z:
            position = the_state.pos_z;
            dimension = "z";
            break;
        default:
            error("broadcast_updated_position called with bad CAN id: %d", can_id);
    }

    can_frame frame = { .can_id = can_id, .can_dlc = 4 };
    float *buffer = (float *) frame.data;
    *buffer = position;

    debug("broadcasting new %s position: %f", dimension, position);
    canframe_sendto(udp_socket(), &frame, sizeof(frame), 0, // no flags
                    broadcast_address, sizeof(broadcast_address));
}

void stop(void) {
    debug("stopping state machine after current iteration\n");
    the_state.T = STOP;
}
