/**
 * Infotainment Server Tests
 * Copyright (C) 2021 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

#ifndef __TEST_CLIENT_H__
#define __TEST_CLIENT_H__

#include <stdbool.h>
#include <stdint.h>

#include "can.h"
#include "infotainment_defs.h"

// the size of the message receive buffer
#define MESSAGE_BUFFER_SIZE 128

// get the UDP socket, creating it if necessary
int udp_socket(void);

// the main event loop
int main_loop(void);

// print a received CAN frame
void print_frame(can_frame *frame);

// print a received position frame
void print_position_frame(can_frame *frame);

// print a received infotainment state frame
void print_infotainment_state_frame(can_frame *frame);

// send a button press
void send_button_press(uint8_t button);

// send a coordinate
void send_coordinate(canid_t dimension, float coordinate);

#endif // __TEST_CLIENT_H__
