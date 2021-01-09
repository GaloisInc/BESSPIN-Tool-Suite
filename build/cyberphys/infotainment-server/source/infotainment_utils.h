/**
 * Infotainment Server Utility Functions
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

#include <unistd.h>

#include "infotainment_defs.h"

/**
 * Get a UDP socket listening on the specified port, creating it if necessary.
 * @param listen_port The port number.
 * @return 0 if successful, error code if not successful
 */
int udp_socket(int listen_port);

/**
 * Get a character (x, y, z) based on the CAN ID for a position dimension.
 * @param dimension_id The CAN ID for the dimension.
 * @return the character.
 */
char char_for_dimension(canid_t dimension_id);

/** 
 * Gets a pointer to the position (in the state) based on the CAN ID for a 
 * position dimension.
 * @param the_state The state to use.
 * @param dimension_id The dimension to find.
 * @return a pointer to the appropriate position float.
 */
float *position_for_dimension(infotainment_state the_state, canid_t dimension_id);

/**
 * Receives a CAN frame sent to the specified port.
 * @param port The port on which to receive.
 * @param buffer The buffer in which to receive the CAN frame.
 * @param buffer_len The length of the CAN frame buffer.
 * @param receive_address The address that the CAN frame came from.
 * @param receive_address_len The length of the address that the CAN frame came from.
 * @return a pointer to the resulting CAN frame, or NULL if no CAN frame was received.
 */
can_frame *receive_frame(int port, uint8_t *buffer, int buffer_len, 
                         struct sockaddr_in *receive_address, 
                         socklen_t *receive_address_len);

/**
 * Broadcasts a CAN frame to the specified port, on all IPv4 interfaces.
 * @param from_port The port to broadcast from.
 * @param to_port The port to broadcast to.
 * @param frame The CAN frame to broadcast.
 * @return The number of bytes sent, or an error code, as from canframe_recvfrom. Note
 * that if more than one broadcast encounters an error, only the lowest error code is
 * returned.
 */
int broadcast_frame(int from_port, int to_port, can_frame *frame);
