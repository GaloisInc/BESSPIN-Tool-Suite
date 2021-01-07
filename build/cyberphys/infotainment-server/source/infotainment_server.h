/**
 * Infotainment Server
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

#ifndef __INFOTAINMENT_SERVER_H__
#define __INFOTAINMENT_SERVER_H__

#include <stdbool.h>
#include <stdint.h>

#include "can.h"
#include "infotainment_defs.h"

// the size of the message receive buffer
#define MESSAGE_BUFFER_SIZE 128

// initialize the server state
bool initialize(void);

// the main event loop
int main_loop(void);

// return true if the CAN ID is relevant to us, false otherwise
bool is_relevant(canid_t can_id);

// update our position based on the CAN frame; return true if the position
// changed, false otherwise
bool update_position(can_frame *frame);

// update our state based on the CAN frame; return true if the state
// changed, false otherwise
bool handle_button_press(can_frame *frame);

// state change for setting the music station
bool set_station(uint8_t station);

// state change for a volume increase button press
bool increase_volume();

// state change for a volume decrease button press
bool decrease_volume();

// broadcast the current music state
void broadcast_music_state(struct sockaddr_in *broadcast_address);

// broadcast an updated position state for the dimension specified in the CAN ID
void broadcast_updated_position(struct sockaddr_in *broadcast_address, canid_t can_id);

// stop the server (e.g., on a Ctrl-C)
void stop(void);

#endif // __INFOTAINMENT_SERVER_H__