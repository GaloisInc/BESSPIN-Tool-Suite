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

/**
 * The size of the message receive buffer.
 */
#define MESSAGE_BUFFER_SIZE 128

/**
 * The main event loop.
 * @return 0 if terminated cleanly; currently, there is no other way
 * to terminate without the program dying.
 */
int main_loop(void);

/**
 * Print a received CAN frame to the console.
 * @param frame The CAN frame.
 */
void print_frame(can_frame *frame);

/**
 * Print a received position CAN frame to the console.
 * @param frame The CAN frame. Must have ID CAN_ID_CAR_X, CAN_ID_CAR_Y, 
 * or CAN_ID_CAR_Z.
 */
void print_position_frame(can_frame *frame);

/**
 * Print a received infotainment state CAN frame to the console.
 * @param frame The CAN frame. Must have ID CAN_ID_INFOTAINMENT_STATE.
 */
void print_music_state_frame(can_frame *frame);

/**
 * Send a button press for the specified button.
 * @param button The button code.
 */
void send_button_press(uint8_t button);

/**
 * Send a coordinate update for the specified dimension.
 * @param dimension_id The dimension CAN ID. Must be CAN_ID_CAR_X,
 * CAN_ID_CAR_Y, or CAN_ID_CAR_Z.
 * @param coordinate The coordinate to send.
 */
void send_coordinate(canid_t dimension_id, float coordinate);

#endif // __TEST_CLIENT_H__
