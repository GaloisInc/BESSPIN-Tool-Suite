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
#include "infotainment_utils.h"
#include "test_client.h"

int main_loop(void) {
    // initialize socket address and buffer data structures
    struct sockaddr_in broadcast_address;
    struct sockaddr_in receive_address;
    socklen_t receive_address_len;
    uint8_t message[MESSAGE_BUFFER_SIZE];
    size_t message_len;
    can_frame *frame;

    return 0;
}

void print_frame(can_frame *frame) {
    switch (frame->can_id) {
        case CAN_ID_CAR_X:
        case CAN_ID_CAR_Y: 
        case CAN_ID_CAR_Z:
            print_position_frame(frame);
            break;
        
        case CAN_ID_MUSIC_STATE:
            print_music_state_frame(frame);
            break;
        
        default:
            debug("irrelevant CAN frame of type %d received.\n", frame->can_id);
    }
}

void print_position_frame(can_frame *frame) {
    // make sure the frame is an appropriate type
    assert(frame->can_id == CAN_ID_CAR_X || frame->can_id == CAN_ID_CAR_Y ||
           frame->can_id == CAN_ID_CAR_Z);

    // interpret the payload as a float
    float *position = (float *) frame->data;
    const char *dimension = "";
    switch (frame->can_id) {
        case CAN_ID_CAR_X:
            dimension = "x";
            break;
        case CAN_ID_CAR_Y:
            dimension = "y";
            break;
        case CAN_ID_CAR_Z:
            dimension = "z";
            break;
    }

    debug("%s-position CAN frame received: %f\n", dimension, *position);
}

void print_music_state_frame(can_frame *frame) {
    // make sure the frame is an appropriate type
    assert(frame->can_id == CAN_ID_MUSIC_STATE);

    debug("music state CAN frame received: playing = %d, station = %d, volume = %d\n",
          play(frame->data[0]), station(frame->data[0]), volume(frame->data[0]));
}

void send_button_press(uint8_t button, struct sockaddr_in *broadcast_address) {
    can_frame frame = { .can_id = CAN_ID_BUTTON_PRESSED, 
                        .can_dlc = BYTE_LENGTH_BUTTON_PRESSED };
    frame.data[0] = button;

    debug("broadcasting button press frame (%d)\n", button);
    canframe_sendto(udp_socket(MUX_PORT), &frame, sizeof(frame), 0, // no flags
                    broadcast_address, sizeof(broadcast_address));
}

void send_coordinate(canid_t dimension_id, float coordinate,
                     struct sockaddr_in *broadcast_address) {
    // make sure the CAN ID is reasonable
    assert(dimension_id == CAN_ID_CAR_X || dimension_id == CAN_ID_CAR_Y ||
           dimension_id == CAN_ID_CAR_Z);

    can_frame frame = { .can_id = dimension_id, .can_dlc = BYTE_LENGTH_CAR_X };
    float *buffer = (float *) frame.data;
    *buffer = coordinate;
    
    char *dimension = "";
    switch (dimension_id) {
        case CAN_ID_CAR_X:
            dimension = "x";
            break;
        case CAN_ID_CAR_Y:
            dimension = "y";
            break;
        case CAN_ID_CAR_Z:
            dimension = "z";
            break;
    }
    debug("broadcasting %s-coordinate update (%f)\n", dimension, coordinate);
    canframe_sendto(udp_socket(MUX_PORT), &frame, sizeof(frame), 0, // no flags
                    broadcast_address, sizeof(broadcast_address));
}

// just run the main loop, no frills
int main(int argc, char** argv) {
    debug("infotainment test client starting\n");
    return main_loop();
}