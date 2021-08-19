/**
 * Hacked Infotainment Server Utility Functions
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

#include <unistd.h>

#include "hacked_defs.h"

/**
 * The number of sockets to cache.
 */
#define SOCKET_CACHE_SIZE 2

/**
 * Get a UDP socket listening on the specified port, creating it if necessary.
 * This function will cache two sockets before killing one to create a new one.
 * @param listen_port The port number.
 * @return 0 if successful, error code if not successful
 */
int udp_socket(int listen_port);

/**
 * Get a character (x, y, z, r) based on the CAN ID for a position dimension.
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
float *position_for_dimension(infotainment_state *the_state, canid_t dimension_id);

/**
 * Receives a CAN frame sent to the specified port. In the returned frame, the CAN ID
 * is in host byte order.
 * 
 * @param socketfd The file descriptor on which to receive.
 * @param port The port that socket is listening on (for self-loop detection).
 * @param buffer The buffer in which to receive the CAN frame.
 * @param buffer_len The length of the CAN frame buffer.
 * @param receive_address The address that the CAN frame came from.
 * @param receive_address_len The length of the address that the CAN frame came from.
 * @return a pointer to the resulting CAN frame, or NULL if no CAN frame was received.
 */
can_frame *receive_frame(int socketfd, int port, uint8_t *buffer, int buffer_len, 
                         struct sockaddr_in *receive_address, 
                         socklen_t *receive_address_len);


/**
 * @return a pointer to the local address as a struct in_addr.
 */
struct in_addr *get_local_address();

/**
 * @return true if the specified address is a valid source for position messages,
 * false otherwise.
 */
bool valid_position_source(struct in_addr address);

/** 
 * Sets the valid position source. If it is not a valid address, any address
 * is considered a valid position source.
 * 
 * @param address The address, as a string.
 */
void set_position_source(char *address);

/**
 * Broadcasts a CAN frame to the specified port, on all IPv4 interfaces.
 * Broadcasts a CAN frame to the specified port, on all IPv4 interfaces. It is assumed
 * that the CAN ID field in the frame is in host byte order.
 *
 * @param from_port The port to broadcast from.
 * @param to_port The port to broadcast to.
 * @param frame The CAN frame to broadcast.
 * @return The number of bytes sent, or an error code, as from canframe_recvfrom. Note
 * that if more than one broadcast encounters an error, only the lowest error code is
 * returned.
 */
int broadcast_frame(int from_port, int to_port, can_frame *frame);

/**
 * Checks to see if the specified address is one of the addresses for the
 * socket created on the specified port.
 * @param port The port of the socket to check.
 * @param address The socket address to check.
 * @return true if the address is one of our addresses, false otherwise.
 */
bool is_our_address(int port, struct sockaddr_in *address);

/**
 * Converts a float from network byte order to local byte order.
 * @param val The float value to convert.
 * @return the converted float value.
 */
float iu_ntohf(float val);

/**
 * Converts a float from local byte order to network byte order.
 * @param val The float value to convert.
 * @return the converted float value.
 */
float iu_htonf(float val);
