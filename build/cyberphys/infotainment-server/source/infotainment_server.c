/**
 * Infotainment Server
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

// general includes
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
infotainment_state the_state = { .S = START };

bool initialize(void) {
    if (the_state.S == RUNNING) {
        error("initialize called on running server");
    }

    // initialize the state; we don't know much initially but
    // we'll set the various fields to sane values
    the_state.V = VOLUME_UNKNOWN;
    the_state.M = MUSIC_UNKNOWN;
    the_state.C = STATION_UNKNOWN;
    the_state.P = POSITION_UNKNOWN;
    the_state.volume = 0;
    the_state.station = 0;
    the_state.pos_x = 0.0f;
    the_state.pos_y = 0.0f;
    the_state.pos_z = 0.0f;
    the_state.S = RUNNING;

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
    
    while (the_state.S == RUNNING) {
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

        broadcast_music_state();
        if (position_updated) {
            broadcast_updated_position(frame->can_id);
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
        debug("updated %s-coordinate to %f\n", dimension, *position);
    }

    return changed;
}

bool handle_button_press(can_frame *frame) {
    return false;
}

void broadcast_music_state() {

}

void broadcast_updated_position(canid_t can_id) {

}

void stop(void) {
    debug("stopping state machine after current iteration\n");
    the_state.S = STOP;
}
