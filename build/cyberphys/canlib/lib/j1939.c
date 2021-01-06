/*
 *  j1939.c
 *  can-transport
 *
 * author: Ethan Lew <elew@galois.com>
 *
 * Higher level protocol to send larger buffers (up to 1785 bytes) over the CAN
 * Bus. Based on J1939 BAM.
 *
 * J1939 BAM sends larger buffer by broadcast a (broadcast announcement message)
 * BAM packet and a sequence of data transfer (DT) packets, containing up to 7
 * bytes.
 *
 * BAM Packet Contents: [0 ctrl byte][1-2 number of bytes][3 number of
 * packets][4 \xFF][5-7 PGN] DT Packet Contents: [0 sequence id][1-7 data]
 */

#include "j1939.h"
#include "can.h"
#include "cyberphys.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#ifndef FREERTOS
    #include <sys/socket.h>
#endif

/**
 * BAM Data Frame Contents
 *
 * packed is needed to make bam_data 8 bytes in length
 */
struct __attribute__((__packed__)) bam_data
{
    uint8_t ctrl_byte;
    uint16_t nbytes;
    uint8_t npackets;
    uint8_t flag;
    uint8_t pgn[3];
} bam_data;

/**
 * DT Data Frame Contents
 */
struct __attribute__((__packed__)) dt_data
{
    uint8_t sequence_index;
    uint8_t data[7];
} dt_data;

canid_t id_from_pgn(uint32_t pgn)
{
    /* NOTE: for J1939, this isn't the correct placement (starts at 9, 18 bits long) */
    uint32_t cid = (pgn & 0x03FFFF) << 7;
    cid |= 0xAA << 24;
    return cid;
}

uint32_t pgn_from_id(canid_t canid)
{
    uint32_t pgn = (canid & (0x03FFFF << 7)) >> 7;
    return pgn;
}

uint8_t test_pgn(uint32_t pgn)
{
    if (pgn > 0x03FFFF)
        return INVALID_PGN;
    return SUCCESS;
}

uint8_t packet_bam(can_frame *cframe, uint16_t nbytes, uint32_t pgn)
{
    /* BAM has a fixed PGN */
    if ((pgn & 0xC0000) != 0)
        return INVALID_PGN;
    cframe->can_id = id_from_pgn(PGN_BAM);

    /* dlc is always 8 */
    cframe->can_dlc = 8;

    uint8_t npackets = nbytes / 7;
    npackets += nbytes % 7 ? 1 : 0;

    /* pack PGN in 3 bytes */
    struct bam_data *bd = (struct bam_data *)cframe->data;
    bd->ctrl_byte = 32;
    bd->nbytes = nbytes;
    bd->npackets = npackets;
    bd->flag = 0xFF;
    bd->pgn[0] = (pgn >> 16) & 0xFF;
    bd->pgn[1] = (pgn >> 8) & 0xFF;
    bd->pgn[2] = (pgn >> 0) & 0xFF;

    return SUCCESS;
}

uint8_t packet_dt(can_frame *cframe, uint8_t sequence_idx, void *data,
                  uint8_t dlen)
{
    cframe->can_id = id_from_pgn(PGN_DT);
    cframe->can_dlc = dlen + 1;
    struct dt_data *dt = (struct dt_data *)cframe->data;

    /* add sequence index to can data */
    dt->sequence_index = sequence_idx;

    /* put data in can packet */
    memcpy(dt->data, data, dlen);

    return SUCCESS;
}

uint8_t params_bam(can_frame *cframe, uint32_t *pgn, uint16_t *nbytes,
                   uint16_t *npackets)
{
    struct bam_data *bd = (struct bam_data *)cframe->data;
    *nbytes = bd->nbytes;
    *npackets = bd->npackets;
    /* pgn is stored in 3 byte array--reconstruct it */
    *pgn = (bd->pgn[0] << 16) | (bd->pgn[1] << 8) | (bd->pgn[2] << 0);
    return SUCCESS;
}

uint8_t params_dt(can_frame *cframe, uint8_t *sequence_idx, void *data,
                  uint8_t *dlen)
{
    *sequence_idx = ((uint8_t *)cframe->data)[0];
    /* TODO: this should be fixed length, but CAN frame enforces it */
    *dlen = 7;
    memcpy(data, (void *)((uint8_t *)cframe->data + 1), (uint32_t)*dlen);
    return SUCCESS;
}

can_frame *data_to_bam_can_frames(uint32_t pgn, void *data, size_t dlen,
                                  uint8_t *npackets)
{
    /* determine number of packets to send */
    uint8_t rnpackets = dlen / 7;
    rnpackets += dlen % 7 ? 1 : 0;
    rnpackets++;
    *npackets = rnpackets;

    /* first packet is the CAN.BAM packet */
    can_frame *packets = (can_frame *)cyberphys_malloc(sizeof(can_frame) * rnpackets);
    packet_bam(&packets[0], dlen, pgn);

    /* put data in the CAN.DT packets */
    uint8_t ll, i;
    for (i = 1; i < rnpackets; i++)
    {
        ll = dlen - (i - 1) * 7;
        ll = (ll >= 7) ? 7 : ll;
        packet_dt(&packets[i], i, (uint8_t *)data + (7 * (i - 1)), ll);
    }

    return packets;
}

void *bam_can_frames_to_data(can_frame *packets)
{
    /* get buffer parameters */
    uint32_t rpgn;
    uint16_t nbytes, npackets;
    params_bam(&packets[0], &rpgn, &nbytes, &npackets);

    /* data to return */
    void *data = cyberphys_malloc(nbytes);

    /* copy over the data from CAN.DT */
    uint8_t ll, i, sidx, slen;
    char ret_data[7];
    for (i = 1; i < npackets + 1; i++)
    {
        params_dt(&packets[i], &sidx, (void *)ret_data, &slen);
        ll = nbytes - (sidx - 1) * 7;
        ll = (ll >= 7) ? 7 : ll;
        memcpy((uint8_t *)data + (sidx - 1) * 7, (void *)ret_data, ll);
    }

    return data;
}

uint8_t send_can_message(cyberphys_socket_t socket, cyberphys_sockaddr_t *dstaddr, uint32_t pgn,
                         void *message, size_t message_len)
{
    if (test_pgn(pgn))
        return INVALID_PGN;
    if (message_len > MAX_MESSAGE_SIZE)
        return INVALID_BUFF_SIZE;

    if (message_len <= 8)
    { /* message fits in a single packet */
        can_frame frame;
        frame.can_id = id_from_pgn(pgn);
        frame.can_dlc = message_len;
        memset(frame.data, 0, sizeof(frame.data));
        memcpy(frame.data, message, message_len);
        /* accounting for smaller messages */
        canframe_sendto(socket, &frame, 5 + message_len, 0,
                        dstaddr, sizeof(*dstaddr));
    }
    else
    { /* message must be sent over multiple packets */
        uint8_t np;
        can_frame *packets = data_to_bam_can_frames(pgn, message, message_len, &np);
        // Note this probably wont work properly with the last packet!
        canframe_sendto(socket, packets, sizeof(can_frame) * (np + 1), 0,
                        dstaddr, sizeof(*dstaddr));
        cyberphys_free(packets);
    }
    return SUCCESS;
}

uint8_t recv_can_message(cyberphys_socket_t socket, cyberphys_sockaddr_t *srcaddr,
                         void *rmessage, size_t *rmessage_len)
{
    int32_t nbytes;
    can_frame *frame;
    char buffer[RECV_BUFF_SIZE];
    socklen_t srclen = sizeof(*srcaddr);
    int flags;

/* recv can frame data */
#ifndef FREERTOS
    flags = MSG_WAITALL;
#else
    flags = 0;
#endif
    nbytes = canframe_recvfrom(socket, (char *)buffer, sizeof(buffer), flags,
                               srcaddr, &srclen);
    printf("Received %i bytes\r\n", nbytes);
    if (nbytes == 0) {
        return EMPTY_RECV;
    }
    if (nbytes <= 0) {
        return ERR_RECV;
    }
    frame = (can_frame *)&buffer[0];

    if (nbytes <= (int32_t)sizeof(can_frame))
    { /* extract data field from single can frame */
        printf("Attempting to decode single frame, rmessage_len =  %u\r\n",frame->can_dlc);
        *rmessage_len = frame->can_dlc;
        /* Check if message len matches the received data*/
        if (frame->can_dlc != (nbytes-5)) {
            return INVALID_LEN;
        }
        /* Check if the CAN ID is correct */
        if ((frame->can_id & 0xFF000000) != 0xAA000000) {
            return INVALID_ID;
        }
        memcpy(rmessage, (void *)&frame->data[0], *rmessage_len);
        return SUCCESS;
    }
    else
    { /* perform multiple can frame protocol */
        if (pgn_from_id(frame->can_id) == PGN_BAM)
        {
            printf("Decoding multiple packets\r\n");
            uint32_t rpgn;
            uint16_t rnbytes, rnpackets;

            /* get bam nbytes, data */
            params_bam(frame, &rpgn, &rnbytes, &rnpackets);
            printf("Got: rpgn: %#X, rnbytes: %u, rnpackets: %u\r\n", rpgn, rnbytes, rnpackets);
            void *rmsg = (void *)bam_can_frames_to_data((can_frame *)buffer);
            *rmessage_len = rnbytes;
            printf("rmessage_len: %u\r\n", rmessage_len);
            memcpy(rmessage, (void *)rmsg, *rmessage_len);
            cyberphys_free(rmsg);
            return SUCCESS;
        }
        else
        { /* no other known protocol */
            printf("Unknown protocol\r\n");
            return UNKNOWN_RECV;
        }
    }
}
