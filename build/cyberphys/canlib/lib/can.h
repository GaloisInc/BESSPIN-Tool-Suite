/*
 * can.h
 * Can Frame/Network Data Types
 *
 * Created by Steven Osborn <steven@lolsborn.com>
*/
#ifndef can_h
#define can_h

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

#ifndef FREERTOS
/**
 * struct can_network - Simulated CAN network over UDP
 * @fd:         network file descriptor
 * @port:       UDP port
 * @servaddr:   network address
 */
typedef struct
{
    int fd;
    int port;
    struct sockaddr_in servaddr;
} can_network;
#endif

#endif /*can_h*/
