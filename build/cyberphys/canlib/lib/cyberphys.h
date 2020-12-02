/*
 * cyberphys.h
 * Cyberphys Multiplatform Functions
 *
 * Created by Ethan Lew on 11/04/20
 */

#ifndef cyberphys_h
#define cyberphys_h

/*
 * Socket, Address Types
 */
#ifndef FREERTOS

#include <sys/socket.h>
#include <unistd.h>
typedef int cyberphys_socket_t;
typedef struct sockaddr_in cyberphys_sockaddr_t;

#else

#include "FreeRTOS.h"
#include "FreeRTOS_IP.h"
#include "FreeRTOS_Sockets.h"
typedef Socket_t cyberphys_socket_t;
typedef struct freertos_sockaddr cyberphys_sockaddr_t;

#endif

/*
 * Cyberphys Multiplatform Memory Allocation
 */
void *cyberphys_malloc(size_t len);

void cyberphys_free(void *ptr);

/*
 * Send CAN frames over Socket
 * Assumes UDP protocol
 */
int32_t cyberphys_sendto(cyberphys_socket_t socket, void *buff, size_t len,
                         int flags, cyberphys_sockaddr_t *dest,
                         socklen_t addr_len);

/*
 * Receive CAN frames over Socket
 * Assumes UDP protocol
 */
int32_t cyberphys_recvfrom(cyberphys_socket_t socket, void *buf, size_t len,
                           int flags, cyberphys_sockaddr_t *src,
                           socklen_t *addr_len);


#endif /* cyberphys_h */
