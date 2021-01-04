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

#include "canlib.h"
#include "cyberphys.h"
#include "j1939.h"

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
    uint8_t message[128];
    size_t message_len;

    // broadcast all outgoing packets to the world (but our world is small)
    broadcast_address.sin_family = AF_INET;
    broadcast_address.sin_port = htons(MUX_PORT);
    broadcast_address.sin_addr.s_addr = htonl(INADDR_BROADCAST);

    debug("socket number is %d\n", udp_socket());
    
    while (the_state.S == RUNNING) {
        // receive a packet
        uint8_t len = recv_can_message(udp_socket(), &receive_address, 
                                       &message, &message_len);

        // decode the packet
        if (len < 0) {
            debug("CAN message receive failed\n");
            continue;
        }
        // change our state based on the packet
        // broadcast the new state
    }

    debug("stop signal received, cleaning up\n");
    // close the UDP socket in an orderly fashion since we're
    // no longer listening
    close(udp_socket());

    return 0;
}

void stop(void) {
    debug("stopping state machine after current iteration\n");
    the_state.S = STOP;
}
