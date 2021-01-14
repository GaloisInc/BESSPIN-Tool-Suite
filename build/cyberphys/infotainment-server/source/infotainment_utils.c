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

int udp_socket(int listen_port) {
    static int socketfd = -1;
    static struct sockaddr_in listen_address;

    // check that the socket is listening on the right port; if not, and if
    // it's still open, close it and make another one
    struct sockaddr_in current_address;
    socklen_t current_len = sizeof(struct sockaddr_in);

    if (getsockname(socketfd, (struct sockaddr *) &current_address, &current_len) == 0) {
        if (ntohs(current_address.sin_port) != listen_port) {
            // it's listening on the wrong port, close it
            debug("closing socket on port %d\n", ntohs(current_address.sin_port));
            close(socketfd);
            socketfd = -1;
        } // else we leave the socket alone
    } else {
        // couldn't get socket status, reset it to -1
        debug("couldn't get socket status for socket %d, errno %d\n", 
              socketfd, errno);
        socketfd = -1;
    }

    // create the socket if it doesn't exist or has been closed     
    if (socketfd < 0 || (fcntl(socketfd, F_GETFD) == -1 && errno != EBADF)) {
        debug("creating socket on port %d\n", listen_port);

        if ((socketfd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)) == -1) {
            error("unable to create socket: error %d\n", errno);
        } 
        
        // initialize the listen address
        memset((char *) &listen_address, 0, sizeof(listen_address));
        listen_address.sin_family = AF_INET;
        listen_address.sin_port = htons(listen_port);
        listen_address.sin_addr.s_addr = htonl(INADDR_ANY);

        // set socket options to receive broadcasts and share address/port
        if (setsockopt(socketfd, SOL_SOCKET, SO_BROADCAST, 
                       &(int){1}, sizeof(int)) < 0) {
            error("unable to set broadcast listening mode\n");
        }
        if (setsockopt(socketfd, SOL_SOCKET, SO_REUSEPORT, 
                       &(int){1}, sizeof(int)) < 0) {
            // this is not fatal but does mean a hack that tries to listen
            // on the same port won't work
            debug("warning: unable to set port reuse mode\n");
        }
        // bind the socket to the port
        if (bind(socketfd, 
                 (struct sockaddr *) &listen_address, 
                 sizeof(listen_address)) == -1) {
            error("unable to listen on port %d\n", listen_port);
        }

        debug("socket created, listening for broadcasts on port %d\n", listen_port);
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

float *position_for_dimension(infotainment_state *the_state, canid_t dimension_id) {
    float *result = NULL;

    switch (dimension_id) {
        case CAN_ID_CAR_X:
            result = &(the_state->pos_x);
            break;
        case CAN_ID_CAR_Y:
            result = &(the_state->pos_y);
            break;
        case CAN_ID_CAR_Z:
            result = &(the_state->pos_z);
            break;
        default:
            error("position_for_dimension called for bad CAN frame type %x\n",
                  dimension_id);
    }
    return result;
}

can_frame *receive_frame(int port, uint8_t *message, int message_len, 
                         struct sockaddr_in *receive_address, 
                         socklen_t *receive_address_len) {
    can_frame *result = NULL;

    while (result == NULL && errno != EINTR) {
        debug("waiting for CAN frame\n");
        *receive_address_len = sizeof(struct sockaddr_in); // must be initialized
        int32_t bytes = recvfrom(udp_socket(port), message, message_len, 0, // no flags
                                 (struct sockaddr *) receive_address,
                                 receive_address_len);

        // if the frame came from us, ignore it; we determine this to be the case if
        // the receive address matches one of our interface addresses _and_ the port
        // number matches the port number of our socket
        if (is_our_address(port, (struct sockaddr_in *) receive_address)) {
            debug("received CAN from from ourselves, ignoring\n");
            continue;
        }

        // decode the packet
        if (bytes < 0) {
            debug("CAN frame receive failed\n");
            continue;
        } else if (bytes == 0) {
            debug("received empty CAN frame\n");
            continue;
        } else if (bytes < 5) {
            debug("received partial CAN frame, ignoring\n");
            continue;
        }

        debug("received %i bytes\n", bytes);
        result = (can_frame *) message;
        if (sizeof(can_frame) < bytes) {
            debug("received (probable) J1939 message, ignoring\n");
            result = NULL;
            continue;
        } else if (result->can_dlc != bytes - 5) {
            debug("received CAN message with invalid length (%d)\n", bytes);
            result = NULL;
            continue;
        }
    }

    return result;
}

int broadcast_frame(int from_port, int to_port, can_frame *frame) {
    int result = 0;

    struct sockaddr_in broadcast_address;
    memset(&broadcast_address, 0, sizeof(struct sockaddr_in));
    broadcast_address.sin_family = AF_INET;
    broadcast_address.sin_port = htons(to_port);
    broadcast_address.sin_addr.s_addr = htonl(INADDR_BROADCAST);

    debug("sending frame to broadcast address %s:%d\n",
        inet_ntoa(broadcast_address.sin_addr), to_port);
    return sendto(udp_socket(from_port), frame, 5 + frame->can_dlc, 0, // no flags
                  (struct sockaddr *) &broadcast_address, 
                  sizeof(struct sockaddr_in));
}

bool is_our_address(int port, struct sockaddr_in *check_address) {
    bool result = false;
    struct ifaddrs *addresses, *addr;

    // get all interfaces
    if (getifaddrs(&addresses) == -1) {
        error("could not get interface addresses (error %d)\n", errno);
    }

    // check each address to see whether it matches
    for (addr = addresses; addr != NULL; addr = addr->ifa_next) {
        if (addr->ifa_addr == NULL || addr->ifa_addr->sa_family != AF_INET) {
            // not an IPv4 address
            continue;
        }
        struct sockaddr_in *our_address = (struct sockaddr_in *) addr->ifa_addr;
        result = result || ((our_address->sin_addr.s_addr - 
                             check_address->sin_addr.s_addr) == 0);
    }

    if (result) {
        // if an address matched, check the port of the socket
        struct sockaddr_in socket_addr;
        socklen_t len = sizeof(struct sockaddr_in);
        if (getsockname(udp_socket(port), 
                        (struct sockaddr *) &socket_addr, &len) == -1) {
            // this isn't fatal, it just means we might receive our own packet
            debug("couldn't get socket info for local socket\n");
            result = false;
        } else {
            result = (check_address->sin_port == socket_addr.sin_port);
        }
    }

    return result;
}