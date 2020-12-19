#include "cyberphys.h"
#include <stdint.h>

#ifndef FREERTOS
/* Unix */
#include <netinet/in.h>
#include <sys/socket.h>
#else
/* FreRTOS */
#include "FreeRTOS_Sockets.h"
#endif

#ifndef FREERTOS
/* Unix */
void *cyberphys_malloc(size_t len) { return malloc(len); }

void cyberphys_free(void *ptr) { return free(ptr); }

int32_t canframe_sendto(cyberphys_socket_t socket, void *buff, size_t len,
                        int flags, cyberphys_sockaddr_t *dest,
                        socklen_t addr_len)
{
    return sendto((int)socket, buff, len, flags, (const struct sockaddr *)dest,
                  addr_len);
}

int32_t canframe_recvfrom(cyberphys_socket_t socket, void *buf, size_t len,
                          int flags, cyberphys_sockaddr_t *src,
                          socklen_t *addr_len)
{
    return recvfrom((int)socket, buf, len, flags, (struct sockaddr *)src,
                    addr_len);
}
#else
/* FreRTOS */
void *cyberphys_malloc(size_t len) { return pvPortMalloc(len); }

void cyberphys_free(void *ptr) { return vPortFree(ptr); }

int32_t canframe_sendto(cyberphys_socket_t socket, void *buf, size_t len,
                        int flags, cyberphys_sockaddr_t *dest,
                        socklen_t addr_len)
{
    return FreeRTOS_sendto(socket,
                           buf,
                           len,
                           flags,
                           dest,
                           addr_len);
}

int32_t canframe_recvfrom(cyberphys_socket_t socket, void *buf, size_t len,
                          int flags, cyberphys_sockaddr_t *src,
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
