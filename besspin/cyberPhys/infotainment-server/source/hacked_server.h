/**
 * Hacked Infotainment Server
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 * 
 * This is the "hacked" version of the infotainment server; it listens only 
 * to the hacker kiosk for control commands, and sends GPS positions
 * back to the hacker kiosk as they are updated on the network. It also 
 * still responds to network heartbeats, so that it will not be killed by
 * an overly-aggressive watchdog.
 */

#ifndef __INFOTAINMENT_SERVER_H__
#define __INFOTAINMENT_SERVER_H__

#include <stdbool.h>
#include <stdint.h>

#include "canlib.h"
#include "hacked_defs.h"

/**
 * The size of the message receive buffer.
 */
#define MESSAGE_BUFFER_SIZE 128

/**
 * Initialize the state machine for the infotainment server.
 * @return true if initialization is successful, false otherwise.
 */
bool initialize(void);

/**
 * The main event loop.
 * @return 0 if terminated cleanly; currently, there is no other way
 * to terminate without the program dying.
 */
int main_loop(void);

/**
 * @param socketfd The socket file descriptor to receive from.
 * @param port The port that file descriptor is listening to (used for self-
 * loop detection on messages).
 */
void receive_from_socket(int socketfd, int port);

/**
 * @param can_id The CAN ID of a message.
 * @return true if the specified CAN ID is relevant to the infotainment
 * server for further processing, false otherwise.
 */
bool is_relevant(canid_t can_id);

/**
 * Update our position based on the specified position CAN frame.
 * @param can_id The CAN frame. Must have ID CAN_ID_CAR_X, CAN_ID_CAR_Y, 
 * or CAN_ID_CAR_Z.
 * @return true if the position was changed, false otherwise.
 */
bool update_position(can_frame *frame);

/**
 * Update our state based on the specified button press CAN frame.
 * @param frame The CAN frame. Must have ID CAN_ID_BUTTON_PRESSED.
 * @return true if the state was changed, false otherwise.
 */
bool handle_button_press(can_frame *frame);

/**
 * State change for setting the music station.
 * @param station The new station number.
 * @return true if the station was changed, false otherwise.
 */
bool set_station(uint8_t station);

/**
 * State change for increasing the volume.
 * @return true if the volume changed, false otherwise.
 */
bool increase_volume();

/**
 * State change for decreasing the volume.
 * @return true if the volume changed, false otherwise.
 */
bool decrease_volume();

/**
 * Broadcast a packet with the current music state (station, volume, playing).
 */
void broadcast_music_state();

/**
 * Broadcast a position update for the appropriate dimension based on the 
 * CAN ID.
 * @param can_id The CAN ID. Must be CAN_ID_CAR_X, CAN_ID_CAR_Y, or 
 * CAN_ID_CAR_Z.
 */
void broadcast_position(canid_t can_id);

/**
 * Broadcast an acknoweledgement to the specified heartbeat request.
 * @param frame The request CAN frame. Must have ID CAN_ID_HEARTBEAT_REQ.
 */
void broadcast_heartbeat_ack(can_frame *frame);

/**
 * Stop the server (typically from a Ctrl-C handler).
 */
void stop(void);

/**
 * Return a valid receive port, based on whether the server is hacked
 */
int get_valid_receive_port(void);

/**
 * Handle new active scenario.
 * If the active scenario is different than the last saved one,
 * re-initialize the server
 */
bool handle_cmd_active_scenario(can_frame *frame);

/**
 * Update the active hack.
 * If the scenario is baseline, and the hack is for infotainment,
 * switch to hacked state.
 */
bool handle_cmd_hack_active(can_frame *frame);

#endif // __INFOTAINMENT_SERVER_H__
