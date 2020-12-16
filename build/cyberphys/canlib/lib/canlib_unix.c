/*
 * unix.c
 * Implementation of Cyberphys Methods for Unix
 *
 * Created by Ethan Lew on 11/04/20
 */
#include "cyberphys.h"
#include <stdlib.h>
#include <sys/socket.h>

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
