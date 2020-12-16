#include "cyberphys.h"
#include <stdint.h>
#include "FreeRTOS_Sockets.h"

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
