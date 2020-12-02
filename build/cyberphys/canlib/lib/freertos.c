#include "cyberphys.h"

void *cyberphys_malloc(size_t len) { return pvPortMalloc(len); }

void cyberphys_free(void *ptr) { return vPortFree(ptr); }

int32_t cyberphys_sendto(cyberphys_socket_t socket, void *buff, size_t len,
                         int flags, cyberphys_sockaddr_t *dest,
                         socklen_t addr_len) {
  return sendto((int)socket, buff, len, flags, (const struct sockaddr *)dest,
                addr_len);
}

int32_t cyberphys_recvfrom(cyberphys_socket_t socket, void *buf, size_t len,
                           int flags, cyberphys_sockaddr_t *src,
                           socklen_t *addr_len) {
  (void) addr_len;
  return FreeRTOS_recvfrom((Socket_t)socket,
                           buf,
                           len,
                           (uint32_t)flags,
                           src,
                           sizeof(struct freertos_sockaddr));
}

int32_t cyberphys_recv(cyberphys_socket_t socket, void *buff, size_t len,
                       int flags) {
  return recv((int)socket, buff, len, flags);
}
