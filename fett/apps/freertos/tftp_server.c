/*
    FreeRTOS V9.0.0 - Copyright (C) 2016 Real Time Engineers Ltd.
    All rights reserved

    VISIT http://www.FreeRTOS.org TO ENSURE YOU ARE USING THE LATEST VERSION.

    This file is part of the FreeRTOS distribution.

    FreeRTOS is free software; you can redistribute it and/or modify it under
    the terms of the GNU General Public License (version 2) as published by the
    Free Software Foundation >>!AND MODIFIED BY!<< the FreeRTOS exception.

    ***************************************************************************
    >>!   NOTE: The modification to the GPL is included to allow you to     !<<
    >>!   distribute a combined work that includes FreeRTOS without being   !<<
    >>!   obliged to provide the source code for proprietary components     !<<
    >>!   outside of the FreeRTOS kernel.                                   !<<
    ***************************************************************************

    FreeRTOS is distributed in the hope that it will be useful, but WITHOUT ANY
    WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
    FOR A PARTICULAR PURPOSE.  Full license text is available on the following
    link: http://www.freertos.org/a00114.html

    ***************************************************************************
     *                                                                       *
     *    FreeRTOS provides completely free yet professionally developed,    *
     *    robust, strictly quality controlled, supported, and cross          *
     *    platform software that is more than just the market leader, it     *
     *    is the industry's de facto standard.                               *
     *                                                                       *
     *    Help yourself get started quickly while simultaneously helping     *
     *    to support the FreeRTOS project by purchasing a FreeRTOS           *
     *    tutorial book, reference manual, or both:                          *
     *    http://www.FreeRTOS.org/Documentation                              *
     *                                                                       *
    ***************************************************************************

    http://www.FreeRTOS.org/FAQHelp.html - Having a problem?  Start by reading
    the FAQ page "My application does not run, what could be wrong?".  Have you
    defined configASSERT()?

    http://www.FreeRTOS.org/support - In return for receiving this top quality
    embedded software for free we request you assist our global community by
    participating in the support forum.

    http://www.FreeRTOS.org/training - Investing in training allows your team to
    be as productive as possible as early as possible.  Now you can receive
    FreeRTOS training directly from Richard Barry, CEO of Real Time Engineers
    Ltd, and the world's leading authority on the world's leading RTOS.

    http://www.FreeRTOS.org/plus - A selection of FreeRTOS ecosystem products,
    including FreeRTOS+Trace - an indispensable productivity tool, a DOS
    compatible FAT file system, and our tiny thread aware UDP/IP stack.

    http://www.FreeRTOS.org/labs - Where new FreeRTOS products go to incubate.
    Come and try FreeRTOS+TCP, our new open source TCP/IP stack for FreeRTOS.

    http://www.OpenRTOS.com - Real Time Engineers ltd. license FreeRTOS to High
    Integrity Systems ltd. to sell under the OpenRTOS brand.  Low cost OpenRTOS
    licenses offer ticketed support, indemnification and commercial middleware.

    http://www.SafeRTOS.com - High Integrity Systems also provide a safety
    engineered and independently SIL3 certified version for use in safety and
    mission critical applications that require provable dependability.

    1 tab == 4 spaces!
*/

/*
 * A basic TFTP server that can currently only be used to receive files, and not
 * send files.  This is a slim implementation intended for use in boot loaders
 * and other applications that require over the air reception of files.
 *
 */

/*
 * For the DARPA FETT Programme, the TFTP Server has been modidied as follows:
 *
 * 1. Received files are placed into an in-memory buffer, not a file.
 * 2. The name of the received file is also placed in an in-memory buffer.
 */

#include "tftp_server.h"

/* Standard includes. */
#include <stdint.h>

/* Fett and FreeRTOS includes. */
#include "fettFreeRTOS.h"

#if (ipconfigALLOW_SOCKET_SEND_WITHOUT_BIND != 1)
#error ipconfigALLOW_SOCKET_SEND_WITHOUT_BIND must be set to one to use this TFTP server.
#endif

//#if (configTICK_RATE_HZ > 1000)
//#error The TFTP server uses the pdMS_TO_TICKS() macro, so configTICK_RATE_HZ must be less than or equal to 1000
//#endif

#ifndef ipconfigTFTP_TIME_OUT_MS
#define ipconfigTFTP_TIME_OUT_MS (10000)
#endif

#ifndef ipconfigTFTP_MAX_RETRIES
#define ipconfigTFTP_MAX_RETRIES (6)
#endif

/* Offset to the file name within the frame. */
#define tftpFILE_NAME_OFFSET (2)

/* Number of bytes in the Ack message. */
#define tftpACK_MESSAGE_LENGTH 4

/* Files are sent in fixed length blocks of 512 (the original maximum). */
#define tftpMAX_DATA_LENGTH ((size_t)512)

/* Standard TFTP opcodes. */
typedef enum
{
    eReadRequest = 1,
    eWriteRequest,
    eData,
    eAck,
    eError
} eTFTPOpcode_t;

/* Error codes from the RFC. */
typedef enum
{
    eFileNotFound = 1,
    eAccessViolation,
    eDiskFull,
    eIllegalTFTPOperation,
    eUnknownTransferID,
    eFileAlreadyExists
} eTFTPErrorCode_t;

/* Header used in data transfer packets. */
#include "pack_struct_start.h"
struct DataPacketHeader
{
    uint16_t usOpcode;
    uint16_t usBlockNumber;
}
#include "pack_struct_end.h"
typedef struct DataPacketHeader TFTPBlockNumberHeader_t;

// A TFTP Write Request has to have a certain minimum lenghh to be valid.
// This server only support "octet" mode, so the minimum length arises with
// a one-character filename "f", thus:
//   "\0 \2 f \0 o c t e t \0"
// which is TEN bytes.
static const int32_t TFTP_Write_Request_Min_Length = 10;

/*
 * Manage the reception of a file.  If the file is received correctly then
 * return pdPASS, otherwise return pdFAIL.
 */
static BaseType_t prvReceiveFile(uint8_t *buffer,     // out
                                 uint32_t buffer_len, // in
                                 uint32_t *file_size, // out
                                 struct freertos_sockaddr *pxClient);

/*
 * Send an error frame to the client.
 */
static void prvSendTFTPError(Socket_t xSocket,
                             struct freertos_sockaddr *pxClient,
                             eTFTPErrorCode_t eErrorCode);

/*
 * Check a received write request contains a potentially valid file name string,
 * and is a binary mode transfer.  If so return a pointer to the file name with
 * the write request packet received from the network, otherwise return NULL.
 * lBytes is the number of bytes on the pucUDPPayloadBuffer received.
 */
static const char *prvValidateWriteRequest(Socket_t xSocket,
                                           struct freertos_sockaddr *pxClient,
                                           uint8_t *pucUDPPayloadBuffer,
                                           int32_t lBytes);

/*
 * Send an acknowledgement packet to pxClient with block number usBlockNumber.
 */
static void prvSendAcknowledgement(Socket_t xSocket,
                                   struct freertos_sockaddr *pxClient,
                                   uint16_t usBlockNumber);

/* The index for the error string below MUST match the value of the applicable
eTFTPErrorCode_t error code value. */
static const char *cErrorStrings[] = {NULL, /* Not valid. */
                                      "File not found.",
                                      "Access violation.",
                                      "Disk full or allocation exceeded.",
                                      "Illegal TFTP operation.",
                                      "Unknown transfer ID.",
                                      "File already exists.",
                                      "No such user."};

/*-----------------------------------------------------------*/

static BaseType_t prvReceiveFile(uint8_t *buffer,     // out
                                 uint32_t buffer_len, // in
                                 uint32_t *file_size, // out
                                 struct freertos_sockaddr *pxClient)
{
    BaseType_t xReturn = pdPASS;
    BaseType_t xRetries = 0;

    Socket_t xTFTPRxSocket = FREERTOS_INVALID_SOCKET;
    TickType_t xRxTimeout = pdMS_TO_TICKS(ipconfigTFTP_TIME_OUT_MS);

    struct freertos_sockaddr xClient;
    uint32_t xClientLength = sizeof(xClient);

    uint16_t usExpectedBlockNumber;
    int32_t lBytes;
    uint8_t *pucFileBuffer;
    TFTPBlockNumberHeader_t *pxHeader;

    size_t xBytesOfFileDataReceived = tftpMAX_DATA_LENGTH;
    size_t Total_Bytes_Written = 0;

    *file_size = 0;

    /* The file is open for writing, now create the socket on which the file
       will be received from the client.  Note the socket is not bound	here - so
       will be automatically bound to a port number selected by the IP stack when
       it is used for the first time. */
    xTFTPRxSocket = FreeRTOS_socket(FREERTOS_AF_INET, FREERTOS_SOCK_DGRAM,
                                    FREERTOS_IPPROTO_UDP);

    if (xTFTPRxSocket != FREERTOS_INVALID_SOCKET)
    {
        /* The socket's Rx block time is set to the user configurable timeout
		value. */
        FreeRTOS_setsockopt(xTFTPRxSocket, 0, FREERTOS_SO_RCVTIMEO, &xRxTimeout,
                            sizeof(xRxTimeout));

        /* Acknowledge the write request so the client starts to send the file.
		The first acknowledgment does not have a corresponding block number so
		the special case block number 0 is used. */
        usExpectedBlockNumber = 0;

        do
        {
            /* The acknowledgment sent here may be a duplicate if the last call
               to FreeRTOS_recvfrom() timee out. */
            prvSendAcknowledgement(xTFTPRxSocket, pxClient,
                                   usExpectedBlockNumber);

            /* Wait for next data packet.  Zero copy is used so it is the
               responsibility of this task to free the received data once it is no
               longer required. */
            lBytes =
                FreeRTOS_recvfrom(xTFTPRxSocket, (void *)&pucFileBuffer, 0,
                                  FREERTOS_ZERO_COPY, &xClient, &xClientLength);

            if (lBytes == 0)
            {
                /* Timed out. */
                fettPrintf("(Error)~  TFTP Timeout.\n");
                xRetries++;

                if (xRetries > ipconfigTFTP_MAX_RETRIES)
                {
                    fettPrintf("(Error)~  TFTP Retry limit exceeded.\n");
                    xReturn = pdFAIL;
                }
            }
            else
            {
                /* Data received.  It is expected to be the next sequential
				block. */
                usExpectedBlockNumber++;
                pxHeader = (TFTPBlockNumberHeader_t *)pucFileBuffer;
                pxHeader->usOpcode = FreeRTOS_ntohs(pxHeader->usOpcode);
                pxHeader->usBlockNumber =
                    FreeRTOS_ntohs(pxHeader->usBlockNumber);

                /* Is the data as expected and from the expected IP address and port? */
                if ((pxHeader->usOpcode == (uint16_t)eData) &&
                    (pxHeader->usBlockNumber == usExpectedBlockNumber) &&
                    (pxClient->sin_addr == xClient.sin_addr) &&
                    (pxClient->sin_port == xClient.sin_port))
                {
                    /* Everything in the packet other than the header is file
					data. */
                    xBytesOfFileDataReceived =
                        (size_t)lBytes - sizeof(TFTPBlockNumberHeader_t);

                    /* Ack the data then write the data to the file. */
                    prvSendAcknowledgement(xTFTPRxSocket, pxClient,
                                           usExpectedBlockNumber);

                    if ((Total_Bytes_Written + xBytesOfFileDataReceived) <=
                        buffer_len)
                    {
                        memcpy(
                            (void *)&buffer[Total_Bytes_Written], // Destination
                            (void *)(pucFileBuffer +
                                     sizeof(TFTPBlockNumberHeader_t)), // Source
                            xBytesOfFileDataReceived); // Number of bytes to copy
                        Total_Bytes_Written += xBytesOfFileDataReceived;
                    }
                    else
                    {
                        fettPrintf("(Info)~  TFTP file too large for receiving "
                                   "buffer\n");
                        // Report "Disk Full" to TFTP Client, although it's really "Buffer Full"
                        prvSendTFTPError(xTFTPRxSocket, pxClient, eDiskFull);
                        xReturn = pdFAIL;
                    }

                    /* Start to receive the next block. */
                    xRetries = 0;
                }
                else
                {
                    prvSendTFTPError(xTFTPRxSocket, pxClient,
                                     eIllegalTFTPOperation);
                    xReturn = pdFAIL;
                }

                /* pucFileBuffer was obtained using zero copy mode, so the
                   buffer must be freed now its contents have been written to the
                   disk. */
                FreeRTOS_ReleaseUDPPayloadBuffer(pucFileBuffer);
            }

            /* Until a disk write fails, or the maximum number of retries is
		  exceeded, or fewer bytes than tftpMAX_DATA_LENGTH are received (which
		  indicates the end of the file). */
        } while ((xReturn != pdFAIL) &&
                 (xBytesOfFileDataReceived == tftpMAX_DATA_LENGTH));

        fettPrintf("(Info)~  TFTP Closing connection.\n");
        FreeRTOS_closesocket(xTFTPRxSocket);
    }
    else
    {
        /* An error could be returned here, but it is probably cleaner to just
		time out as the error would have to be sent via the listening socket
		outside of this function. */
        fettPrintf("(Error)~  TFTP Could not create socket to receive file.\n");
    }

    *file_size = Total_Bytes_Written;
    return xReturn;
}
/*-----------------------------------------------------------*/

void prvSendAcknowledgement(Socket_t xSocket,
                            struct freertos_sockaddr *pxClient,
                            uint16_t usBlockNumber)
{
    /* Small fixed size buffer, so not much to be gained by using the zero copy
interface, just send the buffer directly. */
    TFTPBlockNumberHeader_t xAckMessage;

    xAckMessage.usOpcode = FreeRTOS_htons(((uint16_t)eAck));
    xAckMessage.usBlockNumber = FreeRTOS_htons(usBlockNumber);
    FreeRTOS_sendto(xSocket, (void *)&xAckMessage, tftpACK_MESSAGE_LENGTH, 0,
                    pxClient, sizeof(struct freertos_sockaddr));
}
/*-----------------------------------------------------------*/

static const char *prvValidateWriteRequest(Socket_t xSocket,
                                           struct freertos_sockaddr *pxClient,
                                           uint8_t *pucUDPPayloadBuffer,
                                           int32_t lBytes)
{
    char *pcFileName;
    // Offsets for the parts of the Write Request Header.
    // Since we know lBytes and the only supported mode is "octet", we can
    // compute where "octet" is supposed to begin, and therefore the offset
    // of the \0 character that preceeds it.

    // Request type are at offset 0 and 1, so...
    const int32_t File_Name_Offset = 2;

    // The final byte should be the \0 on the end of "octet" so
    const int32_t Mode_Terminator_Offset = lBytes - 1;
    const int32_t Mode_Offset = lBytes - 6;

    // The byte before the "o" of "octet" should be a \0
    const int32_t File_Name_Terminator_Offset = lBytes - 7;

    bool Terminators_OK;

    // Re-check the pre-condition
    if (lBytes < TFTP_Write_Request_Min_Length)
    {
        fettPrintf("(Error)~  TFTP write request header too short\n");
        prvSendTFTPError(xSocket, pxClient, eIllegalTFTPOperation);
        return NULL;
    }

    pcFileName = (char *)&(pucUDPPayloadBuffer[File_Name_Offset]);

    Terminators_OK =
        (pucUDPPayloadBuffer[File_Name_Terminator_Offset] == 0x00) &&
        (pucUDPPayloadBuffer[Mode_Terminator_Offset] == 0x00);

    if (Terminators_OK)
    {
        bool Mode_OK;

        // RFC 1350 require case-insensitive comparison here
        Mode_OK = (strcasecmp("octet",
                              (const char *)&(
                                  pucUDPPayloadBuffer[Mode_Offset])) == 0);
        if (Mode_OK)
        {
            bool File_Name_OK = true;
            char *p = pcFileName;
            while (*p != 0x00)
            {
                File_Name_OK = File_Name_OK && (*p >= ' ') && (*p <= '~');
                p++;
            }

            if (File_Name_OK)
            {
                size_t fnlen = strlen (pcFileName);

                fettPrintf ("(Info)~  validateWriteRequest pcFileName is %s\n", pcFileName);
                fettPrintf ("(Info)~  validateWriteRequest fnlen is %d\n", (int) fnlen);

                // fnlen needs to be less than MAX to allow for a final \0
                if (fnlen >= tftpconfigMAX_FILENAME)
                {
                    fettPrintf("(Error)~  TFTP filename too long\n");
                    prvSendTFTPError(xSocket, pxClient, eIllegalTFTPOperation);
                    pcFileName = NULL;
                }
                // else everything is fine, so leave pcFileName
                // alone and return it below
            }
            else
            {
                fettPrintf("(Error)~  TFTP illegal character in filename\n");
                prvSendTFTPError(xSocket, pxClient, eIllegalTFTPOperation);
                pcFileName = NULL;
            }
        }
        else
        {
            fettPrintf("(Error)~  TFTP transfer mode is not octet\n");
            prvSendTFTPError(xSocket, pxClient, eIllegalTFTPOperation);
            pcFileName = NULL;
        }
    }
    else
    {
        fettPrintf("(Error)~  TFTP mal-formed write request header\n");
        prvSendTFTPError(xSocket, pxClient, eIllegalTFTPOperation);
        pcFileName = NULL;
    }
    return pcFileName;
}





/*-----------------------------------------------------------*/

static void prvSendTFTPError(Socket_t xSocket,
                             struct freertos_sockaddr *pxClient,
                             eTFTPErrorCode_t eErrorCode)
{
    uint8_t *pucUDPPayloadBuffer = NULL;
    const size_t xFixedSizePart =
        (size_t)5; /* 2 byte opcode, plus two byte error code, plus string terminating 0. */
    const size_t xNumberOfErrorStrings = sizeof(cErrorStrings) / sizeof(char *);
    size_t xErrorCode = (size_t)eErrorCode,
           xTotalLength = 0; /* Only initialised to keep compiler quiet. */
    const char *pcErrorString = NULL;
    int32_t lReturned;

    /* The total size of the packet to be sent depends on the length of the
	error string. */
    if (xErrorCode < xNumberOfErrorStrings)
    {
        pcErrorString = cErrorStrings[xErrorCode];

        /* This task is going to send using the zero copy interface.  The data
           being sent is therefore written directly into a buffer that is passed
           into, rather than copied into, the FreeRTOS_sendto() function.  First
           obtain a buffer of adequate length from the IP stack into which the
           error packet will be written.  Although a max delay is used, the actual
           delay will be capped to ipconfigMAX_SEND_BLOCK_TIME_TICKS. */
        xTotalLength = strlen(pcErrorString) + xFixedSizePart;
        pucUDPPayloadBuffer = (uint8_t *)FreeRTOS_GetUDPPayloadBuffer(
            xTotalLength, portMAX_DELAY);
    }

    if (pucUDPPayloadBuffer != NULL)
    {
        fettPrintf("(Info)~  TFTP %s\n", pcErrorString);

        /* Create error packet: Opcode. */
        pucUDPPayloadBuffer[0] = 0;
        pucUDPPayloadBuffer[1] = (uint8_t)eError;

        /* Create error packet: Error code. */
        pucUDPPayloadBuffer[2] = 0;
        pucUDPPayloadBuffer[3] = (uint8_t)eErrorCode;

        /* Create error packet: Error string. */
        strcpy(((char *)&(pucUDPPayloadBuffer[4])), pcErrorString);

        /* Pass the buffer into the send function.  ulFlags has the
		FREERTOS_ZERO_COPY bit set so the IP stack will take control of the
		buffer rather than copy data out of the buffer. */
        lReturned = FreeRTOS_sendto(
            xSocket, /* The socket to which the error frame is sent. */
            (void *)
                pucUDPPayloadBuffer, /* A pointer to the the data being sent. */
            xTotalLength,            /* The length of the data being sent. */
            FREERTOS_ZERO_COPY, /* ulFlags with the FREERTOS_ZERO_COPY bit set. */
            pxClient,           /* Where the data is being sent. */
            sizeof(*pxClient));

        if (lReturned == 0)
        {
            /* The send operation failed, so this task is still responsible
			for the buffer obtained from the IP stack.  To ensure the buffer
			is not lost it must either be used again, or, as in this case,
			returned to the IP stack using FreeRTOS_ReleaseUDPPayloadBuffer(). */
            FreeRTOS_ReleaseUDPPayloadBuffer((void *)pucUDPPayloadBuffer);
        }
        else
        {
            /* The send was successful so the IP stack is now managing the
			buffer pointed to by pucUDPPayloadBuffer, and the IP stack will
			return the buffer once it has been sent. */
        }
    }
}

#if (DUMMY_TFTP == 1)
#define TEST_PAYLOAD_SIZE 70
static const uint8_t good_one[TEST_PAYLOAD_SIZE] = {
    0xac, 0xa3, 0x99, 0x24, 0x9d, 0xe4, 0x94, 0x20, 0x0f, 0x11, 0xc4, 0xf2,
    0x52, 0x3e, 0xef, 0x90, 0xc3, 0x9e, 0x1f, 0xdb, 0xe3, 0xe5, 0x32, 0x33,
    0x67, 0x23, 0x00, 0xa2, 0xd3, 0x1d, 0xbf, 0x41, 0x4c, 0xcb, 0x2e, 0xb3,
    0x2b, 0xf6, 0x28, 0xef, 0x01, 0x48, 0xe4, 0x81, 0xca, 0x3b, 0xb0, 0xde,
    0x74, 0x07, 0x12, 0xc2, 0xf6, 0x64, 0x5b, 0x34, 0x5b, 0xe9, 0x85, 0x8b,
    0x32, 0xcb, 0x0f, 0x01, 0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x0a};
#endif

uint32_t TFTP_Receive_One_File(uint8_t *buffer,        // out
                               uint32_t buffer_len,    // in
                               char *file_name,        // out
                               uint32_t file_name_len) // in
{
#if (DUMMY_TFTP == 1)
    (void)buffer_len;
    (void)file_name_len;

    // Dummy implementation for testing
    for (int i = 0; i < TEST_PAYLOAD_SIZE; i++)
    {
        buffer[i] = good_one[i];
    }
    file_name[0] = 'f';
    file_name[1] = '\0';
    return TEST_PAYLOAD_SIZE;
#else

    int32_t lBytes;
    uint8_t *pucUDPPayloadBuffer;

    struct freertos_sockaddr xClient;
    struct freertos_sockaddr xBindAddress;

    uint32_t file_size = 0;
    uint32_t xClientLength = sizeof(xClient);
    uint32_t ulIPAddress;

    Socket_t xTFTPListeningSocket;
    BaseType_t Bind_Result;
    BaseType_t Receive_Result = pdPASS;

    const char *pcFileName;

    /* Attempt to open the socket.  The receive block time defaults to the max
     delay, so there is no need to set that separately. */
    xTFTPListeningSocket = FreeRTOS_socket(
        FREERTOS_AF_INET, FREERTOS_SOCK_DGRAM, FREERTOS_IPPROTO_UDP);

    if (xTFTPListeningSocket == FREERTOS_INVALID_SOCKET)
    {
        fettPrintf("(Error)~  TFTP failed to create Listening Socket\n");
        return 0;
    }
    else
    {
        fettPrintf("(Info)~  TFTP created Listening Socket OK\n");
    }

    /* Bind to the standard TFTP port. */
    FreeRTOS_GetAddressConfiguration(&ulIPAddress, NULL, NULL, NULL);
    {
        uint8_t IP_Address_String[16]; // "255.255.255.255\0" is 16 chars
        FreeRTOS_inet_ntoa(ulIPAddress, IP_Address_String);
        fettPrintf("(Info)~  TFTP Target IP address is %s\n", IP_Address_String);
    }

    xBindAddress.sin_addr = ulIPAddress;
    xBindAddress.sin_port = FreeRTOS_htons(TFTP_PORT);
    Bind_Result = FreeRTOS_bind(xTFTPListeningSocket, &xBindAddress,
                                sizeof(xBindAddress));
    if (Bind_Result != 0)
    {
        fettPrintf("(Error)~  TFTP socket bind failed with return code %d\n",
                   (int)Bind_Result);
        return 0;
    }

    /* Look for the start of a new transfer on the TFTP port.  ulFlags has
     the zero copy bit set (FREERTOS_ZERO_COPY) indicating to the stack that
     a reference to the received data should be passed out to this task using
     the second parameter to the FreeRTOS_recvfrom() call.  When this is done
     the IP stack is no longer responsible for releasing the buffer, and the
     task *must* return the buffer to the stack when it is no longer
     needed. */
    fettPrintf("(Info)~  TFTP waiting for initial Request Message\n");
    lBytes = FreeRTOS_recvfrom(
        xTFTPListeningSocket,
        (void *)&pucUDPPayloadBuffer, // out - pointer to data block
        0,                            // not used when FREERTOS_ZERO_COPY
        FREERTOS_ZERO_COPY,           // See above
        &xClient,        // out - Client's source IP address and port number
        &xClientLength); // Not used

    if (lBytes >= 0)
    {
        if (lBytes >= TFTP_Write_Request_Min_Length)
        {
            /* Could this be a new write request?  The opcode is contained in
               the first two bytes of the received data. */
            fettPrintf("(Info)~  TFTP received a request. First header bytes are %2x %2x\n",
                       pucUDPPayloadBuffer[0], pucUDPPayloadBuffer[1]);

            if ((pucUDPPayloadBuffer[0] == (uint8_t)0) &&
                (pucUDPPayloadBuffer[1] == (uint8_t)eWriteRequest))
            {
                /* If the write request is valid pcFileName will get set to
                   point to the file name within pucWriteRequestBuffer - otherwise
                   an appropriate error will be sent on xTFTPListeningSocket. */
                pcFileName = prvValidateWriteRequest(xTFTPListeningSocket, &xClient,
                                                     pucUDPPayloadBuffer, lBytes);

                if (pcFileName != NULL)
                {
                    // Copy the filename from the received request header
                    // to our persistent filename_buffer
                    strncpy(file_name, pcFileName, file_name_len);
                    Receive_Result =
                        prvReceiveFile(buffer, buffer_len, &file_size, &xClient);
                }
            }
            else
            {
                /* Not a transfer ID handled by this server. */
                fettPrintf("(Error)~  TFTP not a Write Request\n");
                prvSendTFTPError(xTFTPListeningSocket, &xClient,
                                 eUnknownTransferID);
            }
        }
        else
        {
            /* message too short. */
            fettPrintf("(Error)~  TFTP initial request message too short\n");
            prvSendTFTPError(xTFTPListeningSocket, &xClient,
                             eUnknownTransferID);
        }

        /* The buffer was received using zero copy, so *must* be freed. */
        FreeRTOS_ReleaseUDPPayloadBuffer(pucUDPPayloadBuffer);
    }
    else
    {
        fettPrintf("(Error)~  TFTP recvfrom() failed with return code %d\n", (int)lBytes);
    }

    fettPrintf("(Info)~  TFTP Closing main listening socket.\n");
    FreeRTOS_closesocket(xTFTPListeningSocket);

    if (Receive_Result == pdFAIL)
    {
        fettPrintf("(Info)~  TFTP File Receive failed. Sanitizing buffers\n");
        memset((void *)buffer, 0, (size_t)buffer_len);
        memset((void *)file_name, 0, (size_t)file_name_len);
        file_size = 0;
    }

    return file_size;
#endif // DUMMY_TFTP
}
