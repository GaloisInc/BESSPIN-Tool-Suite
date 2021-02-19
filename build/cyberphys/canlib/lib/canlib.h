/*
 * canlib.h
 * Can Frame/Network library
 *
 * Created by Steven Osborn <steven@lolsborn.com>,
 * Ethan Lew <elew@galois.com>,
 * Michal Podhradsky <mpodhradsky@galois.com>
*/
#ifndef CANLIB_H
#define CANLIB_H

#ifndef FREERTOS
#include <netinet/in.h>
#endif
#include <stdint.h>

typedef uint32_t canid_t;

/**
 * Controller Area Network Error Frame Mask structure
 *
 * bit 0-28	: error class mask (see include/linux/can/error.h)
 * bit 29-31	: set to zero
 */
typedef uint32_t can_err_mask_t;

/**
 * struct can_frame - basic CAN frame structure
 * @can_id:  the CAN ID of the frame and CAN_*_FLAG flags, see above.
 * @can_dlc: the data length field of the CAN frame
 * @data:    the CAN frame payload.
 */
#pragma pack(1)
typedef struct
{
    canid_t can_id;  /* 32 bit CAN_ID + EFF/RTR/ERR flags */
    uint8_t can_dlc; /* data length code: 0 .. 8 */
    uint8_t data[8] __attribute__((aligned(8)));
} can_frame;
#pragma pack(0)

/*
 * Socket, Address Types
 */
#ifndef FREERTOS

#include <sys/socket.h>
#include <unistd.h>
typedef int canlib_socket_t;
typedef struct sockaddr_in canlib_sockaddr_t;

#else

#include "FreeRTOS.h"
#include "FreeRTOS_Sockets.h"
#include "FreeRTOS_IP.h"
typedef Socket_t canlib_socket_t;
typedef struct freertos_sockaddr canlib_sockaddr_t;

#endif /* FREERTOS */

uint32_t canlib_ntohl(uint32_t val);

uint32_t canlib_htonl(uint32_t val);

/**
 * canlib Multiplatform Memory Allocation
 */
void *canlib_malloc(size_t len);

/**
 * canlib Multiplatform Memory Deallocation
 */
void canlib_free(void *ptr);

/**
 * Send CAN frames over Socket
 * Assumes UDP protocol
 * @returns number of bytes sent, or error code
 */
int32_t canframe_sendto(canlib_socket_t socket, void *buff, size_t len,
                         int flags, canlib_sockaddr_t *dest,
                         socklen_t addr_len);

/**
 * Receive CAN frames over Socket
 * Assumes UDP protocol, socket bound to a particular port
 * @returns number of bytes received, or error code
 */
int32_t canframe_recvfrom(canlib_socket_t socket, void *buf, size_t len,
                           int flags, canlib_sockaddr_t *src,
                           socklen_t *addr_len);

#endif /* CANLIB_H */
