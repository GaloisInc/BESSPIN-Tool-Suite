/*
 * CAN Packet UDP Server
 *
 * author: Ethan Lew <elew@galois.com>
 *
 * Listen for CAN packets over UDP. The server also checks if the CAN packet
 * contains the BAM J1939 higher order protocol, and will reconstruct and
 * print the buffer if so.
 */
#include "can.h"
#include "j1939.h"
#include <netinet/in.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT 8080
#define BUF_SIZE 4096

int main(int argc, char *argv[]) {
  int sockfd, broadcast, nbytes;
  size_t blen;
  struct sockaddr_in servaddr;

  if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
    perror("socket creation failed");
    exit(EXIT_FAILURE);
  }

  servaddr.sin_family = AF_INET;
  servaddr.sin_addr.s_addr = INADDR_ANY;
  servaddr.sin_port = htons(PORT);
  broadcast = 1;

  if (bind(sockfd, (const struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
    perror("bind failed");
    exit(EXIT_FAILURE);
  }

  if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast,
                 sizeof(broadcast)) < 0) {
    perror("socket configuration failed");
    close(sockfd);
    exit(EXIT_FAILURE);
  }

  /* allocate return message buffer
   * this is where the hack could happen -- overflow this buffer
   */
  char rbuff[128];

  while (1) {
    recv_can_message(sockfd, rbuff, &blen);
    printf("Recv %d bytes ", (uint32_t)blen);
    printf("Received message: \"");
    for (uint i = 0; i < blen; i++) putchar(rbuff[i]);
    printf("\"\n");
  }

  /* close and free */
  close(sockfd);
  free(rbuff);

  return 0;
}
