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

#define PORT 5001
#define PGN 60879
#define TARGET_ADDR "10.88.88.11"

int main(int argc, char *argv[])
{
    const char msg[] = "This is a message from J1939 client: Hello World";

    /* setup the socket to broadcast */
    int sockfd, broadcast;
    uint8_t buffer[128];
    //cyberphys_sockaddr_t servaddr;
    struct sockaddr_in servaddr;

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    /*
    broadcast = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast,
                   sizeof(broadcast)) < 0)
    {
        perror("socket configuration failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }
    */

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(PORT);
    inet_pton(AF_INET, TARGET_ADDR, &servaddr.sin_addr.s_addr);


    printf("servaddr.sin_addr.s_addr: %u\r\n", servaddr.sin_addr.s_addr);

    uint8_t res = send_can_message(sockfd, &servaddr, PGN, (void *)&msg, sizeof(msg));
    //ssize_t res = sendto(sockfd, msg, sizeof(msg), 0, (const struct sockaddr *)&servaddr, sizeof(servaddr));
    printf("response: %u\t\n", res);

    /* close and free */
    close(sockfd);

    printf("Done\n");
    return 0;
}