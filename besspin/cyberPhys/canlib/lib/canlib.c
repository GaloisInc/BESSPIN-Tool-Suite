#include "canlib.h"
#include <stdint.h>

#ifndef FREERTOS
/* Unix */
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <stdlib.h>
#else
/* FreRTOS */
#include "FreeRTOS_Sockets.h"
#endif

#ifndef FREERTOS
/* Unix */
uint32_t canlib_ntohl(uint32_t val)
{
    return ntohl(val);
}

uint32_t canlib_htonl(uint32_t val)
{
    return htonl(val);
}

uint32_t canlib_ntohl(uint32_t val);
void *canlib_malloc(size_t len) { return malloc(len); }

void canlib_free(void *ptr) { return free(ptr); }

int32_t canframe_sendto(canlib_socket_t socket, void *buff, size_t len,
                        int flags, canlib_sockaddr_t *dest,
                        socklen_t addr_len)
{
    return sendto((int)socket, buff, len, flags, (const struct sockaddr *)dest,
                  addr_len);
}

int32_t canframe_recvfrom(canlib_socket_t socket, void *buf, size_t len,
                          int flags, canlib_sockaddr_t *src,
                          socklen_t *addr_len)
{
    return recvfrom((int)socket, buf, len, flags, (struct sockaddr *)src,
                    addr_len);
}
#else
/* FreRTOS */
uint32_t canlib_ntohl(uint32_t val)
{
    return FreeRTOS_ntohl(val);
}

uint32_t canlib_htonl(uint32_t val)
{
    return FreeRTOS_htonl(val);
}
void *canlib_malloc(size_t len) { return pvPortMalloc(len); }

void canlib_free(void *ptr) { return vPortFree(ptr); }

int32_t canframe_sendto(canlib_socket_t socket, void *buf, size_t len,
                        int flags, canlib_sockaddr_t *dest,
                        socklen_t addr_len)
{
    return FreeRTOS_sendto(socket,
                           buf,
                           len,
                           flags,
                           dest,
                           addr_len);
}

int32_t canframe_recvfrom(canlib_socket_t socket, void *buf, size_t len,
                          int flags, canlib_sockaddr_t *src,
                          socklen_t *addr_len)
{
    return FreeRTOS_recvfrom((Socket_t)socket,
                             buf,
                             len,
                             flags,
                             src,
                             addr_len);
}
#endif
