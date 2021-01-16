/**
 * Infotainment Server Tests
 * Copyright (C) 2021 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

// NOTE: We assume that the infotainment server under test is the only other
// entity sending CAN packets on the network; the expected numbers and ordering
// of response packets will not work otherwise. Thus, these tests are only 
// useful for testing the infotainment server in isolation, not while running 
// in a full system.
//
// This test client _sends_ packets to the RECEIVE_PORT, and _listens_
// on the SEND_PORT, so as to communicate with the server properly. If 
// SEND_PORT and RECEIVE_PORT are the same, testing cannot be carried out
// on the same machine as the server because of the same IP addresses and
// port numbers being used.

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
#include "infotainment_utils.h"
#include "test_client.h"

int main_loop(void) {
    // initialize socket address and buffer data structures
    struct sockaddr_in broadcast_address;
    struct sockaddr_in receive_address;
    socklen_t receive_address_len;
    uint8_t message[MESSAGE_BUFFER_SIZE];
    can_frame *frame;

    // broadcast all outgoing packets to the world (but our world is small)
    broadcast_address.sin_family = AF_INET;
    broadcast_address.sin_port = htons(RECEIVE_PORT);
    broadcast_address.sin_addr.s_addr = htonl(INADDR_BROADCAST);

    debug("socket number is %d\n", udp_socket(SEND_PORT));


    // zero out the buffer
    memset(&message, 0, MESSAGE_BUFFER_SIZE);

    // send enough frames to initialize the infotainment system to a known state;
    // we expect one response for each frame we send, including the position 
    // setting (which we expect to always be a change from the initial position
    // of 0.0f, 0.0f, 0.0f).
    send_button_press(BUTTON_STATION_1);
    print_frame(receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                              &receive_address, &receive_address_len));
    send_coordinate(CAN_ID_CAR_X, 1.0f);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_position(frame, CAN_ID_CAR_X, 1.0f);

    send_coordinate(CAN_ID_CAR_Y, 1.0f);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_position(frame, CAN_ID_CAR_Y, 1.0f);

    send_coordinate(CAN_ID_CAR_Z, 1.0f);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_position(frame, CAN_ID_CAR_Z, 1.0f);

    send_coordinate(CAN_ID_CAR_R, 1.0f);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_position(frame, CAN_ID_CAR_R, 1.0f);

    for (int i = 0; i < MAX_VOLUME + 2; i++) {
        // lower the volume to 0 no matter what it started at; this also tests
        // min volume
        send_button_press(BUTTON_VOLUME_DOWN);
        frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE,
                              &receive_address, &receive_address_len);
        print_frame(frame);
    }

    // the final music state frame should have music on, station 1, 
    // volume MIN_VOLUME
    assert_music_state(frame, 1, 1, MIN_VOLUME);

    // test volume up
    send_button_press(BUTTON_VOLUME_UP);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE,
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_music_state(frame, 1, 1, MIN_VOLUME + 1);

    // test volume down
    send_button_press(BUTTON_VOLUME_DOWN);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE,
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_music_state(frame, 1, 1, MIN_VOLUME);

    // test volume all the way up (max volume)
    for (int i = 0; i < MAX_VOLUME + 2; i++) {
        send_button_press(BUTTON_VOLUME_UP);
        frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE,
                              &receive_address, &receive_address_len);
        print_frame(frame);
    }
    assert_music_state(frame, 1, 1, MAX_VOLUME);

    // test station 2 (station 1 was already tested)
    send_button_press(BUTTON_STATION_2);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE,
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_music_state(frame, 1, 2, MAX_VOLUME);

    // test station 3
    send_button_press(BUTTON_STATION_3);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE,
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_music_state(frame, 1, 3, MAX_VOLUME);

    // test sending redundant position changes for x, y followed by a position
    // change for z; only the z one should result in a packet
    send_coordinate(CAN_ID_CAR_X, 1.0f);
    send_coordinate(CAN_ID_CAR_Y, 1.0f);
    send_coordinate(CAN_ID_CAR_Z, 1.1f); // one of these is not like the others
    send_coordinate(CAN_ID_CAR_R, 1.0f);

    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_position(frame, CAN_ID_CAR_Z, 1.1f);

    // send position updates back to 0.0 for all coordinates so we can run
    // the tests again without restarting the server
    send_coordinate(CAN_ID_CAR_X, 0.0f);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_position(frame, CAN_ID_CAR_X, 0.0f);

    send_coordinate(CAN_ID_CAR_Y, 0.0f);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_position(frame, CAN_ID_CAR_Y, 0.0f);

    send_coordinate(CAN_ID_CAR_Z, 0.0f);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_position(frame, CAN_ID_CAR_Z, 0.0f);

    send_coordinate(CAN_ID_CAR_R, 0.0f);
    frame = receive_frame(SEND_PORT, message, MESSAGE_BUFFER_SIZE, 
                          &receive_address, &receive_address_len);
    print_frame(frame);
    assert_position(frame, CAN_ID_CAR_R, 0.0f);

    debug("\n\nTESTS SUCCESSFUL\n");
    return 0;
}

void assert_music_state(can_frame *frame, int play, int station, int volume) {
    assert(frame->can_id == CAN_ID_MUSIC_STATE);
    assert(play(frame->data[0]) == play);
    assert(station(frame->data[0]) == station);
    assert(volume(frame->data[0]) == volume);
}

void assert_position(can_frame *frame, canid_t dimension_id, float position) {
    assert(frame->can_id == dimension_id);
    float *frame_position = (float *) frame->data;
    assert(*frame_position == position);
}

void print_frame(can_frame *frame) {
    if (frame == NULL) {
        debug("null frame received\n");

    } else {
    switch (frame->can_id) {
            case CAN_ID_CAR_X:
            case CAN_ID_CAR_Y: 
            case CAN_ID_CAR_Z:
            case CAN_ID_CAR_R:
                print_position_frame(frame);
                break;
        
            case CAN_ID_MUSIC_STATE:
                print_music_state_frame(frame);
                break;

            default:
                debug("irrelevant CAN frame with id %x received.\n", frame->can_id);
        }
    }
}

void print_position_frame(can_frame *frame) {
    // make sure the frame is an appropriate type
    assert(frame->can_id == CAN_ID_CAR_X || frame->can_id == CAN_ID_CAR_Y ||
           frame->can_id == CAN_ID_CAR_Z || frame->can_id == CAN_ID_CAR_R);

    // interpret the payload as a float
    float *position = (float *) frame->data;

    debug("%c-position CAN frame received: %f\n", 
          char_for_dimension(frame->can_id), *position);
}

void print_music_state_frame(can_frame *frame) {
    // make sure the frame is an appropriate type
    assert(frame->can_id == CAN_ID_MUSIC_STATE);

    debug("music state CAN frame received: raw = %d, playing = %d, station = %d, volume = %d\n",
          frame->data[0], play(frame->data[0]), 
          station(frame->data[0]), volume(frame->data[0]));
}

void send_button_press(uint8_t button) {
    can_frame frame = { .can_id = CAN_ID_BUTTON_PRESSED, 
                        .can_dlc = BYTE_LENGTH_BUTTON_PRESSED };
    frame.data[0] = button;

    debug("broadcasting button press frame (%d)\n", button);
    broadcast_frame(SEND_PORT, RECEIVE_PORT, &frame);
}

void send_coordinate(canid_t dimension_id, float coordinate) {
    // make sure the CAN ID is reasonable
    assert(dimension_id == CAN_ID_CAR_X || dimension_id == CAN_ID_CAR_Y ||
           dimension_id == CAN_ID_CAR_Z || dimension_id == CAN_ID_CAR_R);

    can_frame frame = { .can_id = dimension_id, .can_dlc = BYTE_LENGTH_CAR_X };
    float *buffer = (float *) frame.data;
    *buffer = coordinate;
    
    debug("broadcasting %c-coordinate update (%f)\n", 
          char_for_dimension(dimension_id), coordinate);
    broadcast_frame(SEND_PORT, RECEIVE_PORT, &frame);
}

// just run the main loop, no frills
int main(int argc, char** argv) {
    debug("infotainment test client starting\n");
    return main_loop();
}