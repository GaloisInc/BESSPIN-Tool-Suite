/**
 * Infotainment Server Tests
 * Copyright (C) 2021 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

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
#include "test_client.h"

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
        listen_address.sin_port = htons(MUX_PORT);
        listen_address.sin_addr.s_addr = htonl(INADDR_ANY);

        // bind the socket to the port
        if (bind(socketfd, 
                 (struct sockaddr *) &listen_address, 
                 sizeof(listen_address)) == -1) {
            error("unable to listen on mux port (%d)\n", 
                  MUX_PORT);
        }

        // set socket options to receive broadcasts
        int broadcast_permission = 1;
        if (setsockopt(socketfd, SOL_SOCKET, SO_BROADCAST, (void *) &broadcast_permission, 
                       sizeof(broadcast_permission)) < 0) {
            error("unable to set broadcast listening mode\n");
        }

        debug("socket created, listening for broadcasts on mux port (%d)\n", 
              MUX_PORT);
    }

    return socketfd;   
}

int main_loop(void) {
    return 0;
}

void print_frame(can_frame *frame) {
    switch (frame->can_id) {
        case CAN_ID_CAR_X:
        case CAN_ID_CAR_Y: 
        case CAN_ID_CAR_Z:
            print_position_frame(frame);
            break;
        
        case CAN_ID_INFOTAINMENT_STATE:
            print_infotainment_state_frame(frame);
            break;
        
        default:
            debug("irrelevant CAN frame of type %d received.\n", frame->can_id);
    }
}

void print_position_frame(can_frame *frame) {

}

void print_infotainment_state_frame(can_frame *frame) {

}

void send_button_press(uint8_t button) {

}

void send_coordinate(canid_t dimension, float coordinate) {

}

// just run the main loop, no frills
int main(int argc, char** argv) {
    debug("infotainment test client starting\n");
    return main_loop();
}