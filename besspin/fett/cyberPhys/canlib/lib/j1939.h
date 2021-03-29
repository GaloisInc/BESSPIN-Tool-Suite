/*
 *  j1939.h
 *  can-transport
 *
 *  Created by Ethan Lew on 10/22/20.
 */

#ifndef j1939_h
#define j1939_h

#include "canlib.h"
#include <stdio.h>

#define PGN_BAM 60416
#define PGN_DT 60160
#define RECV_BUFF_SIZE 512
#define MAX_MESSAGE_SIZE 1785

/**
 * J1939 status
 */
typedef enum {
  SUCCESS = 0,
  INVALID_PGN = 1,
  INVALID_BUFF_SIZE = 2,
  UNKNOWN_RECV = 3,
  INVALID_LEN = 4,
  INVALID_ID = 5,
  ERR_RECV = 6,
  EMPTY_RECV = 7,
  ERR_SEND = 8
} j1939_status;

/**
 * Translates a CAN ID to an acceptable PGN
 * NOTE: this doesn't use the rest of the CAN J1939 standard appropriately
 * @returns can id
 */
canid_t id_from_pgn(uint32_t pgn);

/**
 * Extracts the PGN from a CAN ID
 * @returns pgn
 */
uint32_t pgn_from_id(canid_t canid);

/**
 * Determines if a 32 bit number is a valid PGN
 * @returns SUCCESS or INVALID_PGN
 */
uint8_t test_pgn(uint32_t pgn);

/**
 * CAN frame for J1939 TP.BAM
 * @returns error code
 */
uint8_t packet_bam(can_frame *cframe, uint16_t nbytes, uint32_t pgn);

/**
 * CAN frame for J1939 TP.DT
 * @returns error code
 */
uint8_t packet_dt(can_frame *cframe, uint8_t sequence_idx, void *data, uint8_t dlen);


/**
 * Get J1939 TP.BAM parameters
 * @returns error code
 */
uint8_t params_bam(can_frame *cframe, uint32_t *pgn, uint16_t *nbytes, uint16_t *npackets);

/**
 * Get J1939 TP.DT parameters
 * @returns error code
 */
uint8_t params_dt(can_frame *cframe, uint8_t *sequence_idx, void *data, uint8_t *dlen);

/**
 * Convert buffer into an array of CAN frames
 * @returns array of CAN frames
 */
can_frame *data_to_bam_can_frames(uint32_t pgn, void *data, size_t dlen, uint8_t *npackets);

/**
 * Reconstruct buffer from an array of CAN frames
 * @returns error code
 */
void *bam_can_frames_to_data(can_frame *packets);

/**
 * send message over socket as can frames, using J1939 BAM if message length is
 * greater than 8 bytes
 * @param pgn_or_id - if message_len <= 8 it is interpreted as CAN_ID, otherwise as PGN
 * @returns error code
 */
uint8_t send_can_message(canlib_socket_t socket,
                         canlib_sockaddr_t *dstaddr,
                         uint32_t pgn_or_id,
                         void *message,
                         size_t message_len);

/**
  * reconstruct a message from can frames sent using send_can_message
  * @returns error code
  */
uint8_t recv_can_message(canlib_socket_t socket,
                         canlib_sockaddr_t *srcaddr,
                         canid_t *can_id,
                         void *rmessage,
                         size_t *rmessage_len);

#endif /* j1939_h */
