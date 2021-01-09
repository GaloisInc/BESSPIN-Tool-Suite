/**
 * Infotainment Server Utility Functions
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

#include <assert.h>
#include <errno.h>
#include <fcntl.h>
#include <ifaddrs.h>
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
#include "infotainment_utils.h"

int udp_socket(int port) {
    static int socketfd = -1;
    static struct sockaddr_in listen_address;

    // check that the socket is listening on the right port; if not, and if
    // it's still open, close it and make another one
    struct sockaddr_in current_address;
    socklen_t current_len;

    if (getsockname(socketfd, (struct sockaddr *) &current_address, &current_len) == 0) {
        if (current_address.sin_port != htons(port)) {
            // it's listening on the wrong port, close it
            debug("closing socket on port %d\n", ntohs(current_address.sin_port));
            close(socketfd);
            socketfd = -1;
        } // else we leave the socket alone
    } else {
        // couldn't get socket status, reset it to -1
        socketfd = -1;
    }

    // create the socket if it doesn't exist or has been closed     
    if (socketfd < 0 || (fcntl(socketfd, F_GETFD) == -1 && errno != EBADF)) {
        debug("creating socket on port %d\n", port);

        if ((socketfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
            error("unable to create socket: error %d\n", errno);
        } 
        
        // initialize the listen address
        memset((char *) &listen_address, 0, sizeof(listen_address));
        listen_address.sin_family = AF_INET;
        listen_address.sin_port = htons(port);
        listen_address.sin_addr.s_addr = htonl(INADDR_ANY);

        // bind the socket to the port
        if (bind(socketfd, 
                 (struct sockaddr *) &listen_address, 
                 sizeof(listen_address)) == -1) {
            error("unable to listen on port %d\n", port);
        }

        // set socket options to receive broadcasts
        int broadcast_permission = 1;
        if (setsockopt(socketfd, SOL_SOCKET, SO_BROADCAST, (void *) &broadcast_permission, 
                       sizeof(broadcast_permission)) < 0) {
            error("unable to set broadcast listening mode\n");
        }

        debug("socket created, listening for broadcasts on port %d\n", port);
    }

    return socketfd;   
}

char char_for_dimension(canid_t dimension_id) {
    char result = '?';

    switch (dimension_id) {
        case CAN_ID_CAR_X:
            result = 'x';
            break;
        
        case CAN_ID_CAR_Y:
            result = 'y';
            break;

        case CAN_ID_CAR_Z:
            result = 'z';
            break;

        default:
            debug("char_for_dimension called for bad CAN frame type %x\n", dimension_id);
    }

    return result;
}

float *position_for_dimension(infotainment_state the_state, canid_t dimension_id) {
    float *result = NULL;

    switch (dimension_id) {
        case CAN_ID_CAR_X:
            result = &the_state.pos_x;
            break;
        case CAN_ID_CAR_Y:
            result = &the_state.pos_y;
            break;
        case CAN_ID_CAR_Z:
            result = &the_state.pos_z;
            break;
        default:
            debug("position_for_dimension called for bad CAN farme type %x\n", dimension_id);
    }

    return result;
}

can_frame *receive_frame(int port, uint8_t *message, int message_len, 
                         struct sockaddr_in *receive_address, 
                         socklen_t *receive_address_len) {
    can_frame *result = NULL;

    while (result == NULL && errno != EINTR) {
        debug("waiting for CAN frame\n");
        int32_t bytes = recvfrom(udp_socket(port), message, message_len, 0, // no flags
                                 (struct sockaddr *) receive_address, receive_address_len);

        // decode the packet
        if (bytes < 0) {
            debug("CAN frame receive failed\n");
            continue;
        } else if (bytes == 0) {
            debug("received empty CAN frame\n");
            continue;
        }

        debug("received %i bytes\n", bytes);
        result = (can_frame *) message;
        if (bytes <= sizeof(can_frame) && (result->can_dlc != bytes - 5)) {
            debug("received CAN message with invalid length (%d)\n", bytes);
            result = NULL;
            continue;
        } else {
            debug("received (probable) J1939 message, ignoring\n");
            result = NULL;
            continue;
        }
    }

    return result;
}

int32_t broadcast_frame(int from_port, int to_port, can_frame *frame) {
    struct ifaddrs *addresses, *addr;
    int32_t result = 0x7fffffff; // maximum value for a signed 32-bit int

    // get all interfaces
    if (getifaddrs(&addresses) == -1) {
        error("could not get interface addresses (error %d), exiting\n", errno);
    }

    // broadcast to every one of our broadcast addresses
    for (addr = addresses; addr != NULL; addr = addr->ifa_next) {
        if (addr->ifa_addr == NULL || addr->ifa_addr->sa_family != AF_INET ||
            addr->ifa_broadaddr == NULL) {
            // empty or non-IPv4 address, or empty broadcast address
            continue;
        } 
        
        struct sockaddr_in *broadcast_address = (struct sockaddr_in *) addr->ifa_broadaddr;
        broadcast_address->sin_port = htons(to_port);

        debug("sending frame to broadcast address %s\n", 
              inet_ntoa(broadcast_address->sin_addr));
        int32_t bytes = 
            sendto(udp_socket(from_port), frame, sizeof(can_frame), 0, // no flags
                   (struct sockaddr *) broadcast_address, sizeof(broadcast_address));
        if (bytes < result) {
            result = bytes; // always return the lowest error code
        }
    }  

    freeifaddrs(addresses);
    return result;
}