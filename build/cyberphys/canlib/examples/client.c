/*
 * J1939 UDP Client Example Program
 *
 * author: Ethan Lew <elew@galois.com>
 *
 * Send a message over UDP using the CAN J1939 BAM protocol
 */
#include "can.h"
#include "cyberphys.h"
#include "j1939.h"
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT 8080
#define MSG_CONFIRM 0
#define PGN 60879

int main(int argc, char *argv[]){
  const char msg[] = "This is a message from J1939 client: Hello World";

  /* setup the socket to broadcast */
  int sockfd, broadcast;
  uint8_t buffer[128];
  cyberphys_sockaddr_t servaddr;

  if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
    perror("socket creation failed");
    exit(EXIT_FAILURE);
  }

  broadcast = 1;
  if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast,
                 sizeof(broadcast)) < 0) {
    perror("socket configuration failed");
    close(sockfd);
    exit(EXIT_FAILURE);
  }

  memset(&servaddr, 0, sizeof(servaddr));
  servaddr.sin_family = AF_INET;
  servaddr.sin_port = htons(PORT);
  servaddr.sin_addr.s_addr = INADDR_ANY;


  /* send an unrelated packet */
  can_frame frame = {1, 2, "adsf0000"};
  send_can_message(sockfd, servaddr, PGN, (void *)"adsf0000", 8);
  send_can_message(sockfd, servaddr, PGN, (void *)&msg, sizeof(msg));

  /* close and free */
  close(sockfd);

  return 0;
}
