// This is the main task executed by ota

#include "fettFreeRTOS.h"
#include "ota_common.h"
#include "ota_tests.h"
#include "tftp_server.h"

#define OTA_FILE_MIN_SIZE (ED25519_SIG_SIZE + 1)

static intptr_t wptl = 0;

uint8_t file_buffer[OTA_MAX_SIGNED_PAYLOAD_SIZE]; // SIZE set in setupEnv.json

/* Sets file_buffer[0 .. OTA_MAX_SIGNED_PAYLOAD_SIZE-1] to all zero bytes */
void Initialize_Receipt_Buffer(void);

/* Writes file_buffer[ED25519_SIG_SIZE .. ED25519_SIG_SIZE+fsize-1] to the log */
void Write_Payload_To_Log(size_t fsize);

/* Writes file_buffer[ED25519_SIG_SIZE .. ED25519_SIG_SIZE+fsize-1] to the filesystem */
void Write_Payload_To_FS(size_t fsize);

void Receive_And_Process_One_OTA_Request(ed25519_key *pk);

void Ota_Worker(ed25519_key *pk);

void vOta(void *pvParameters);


// This is the Public Key used for Ed25519 signature verification
static const byte raw_pk[ED25519_KEY_SIZE] = {
    0xBA, 0xFB, 0xD4, 0xBB, 0x9F, 0x8E, 0xCE, 0xC1, 0xEC, 0xE7, 0x42,
    0xD7, 0xEA, 0x3B, 0x2E, 0xE2, 0xE0, 0x16, 0xE3, 0x0F, 0x27, 0x0B,
    0xAE, 0x74, 0xB3, 0x0B, 0xED, 0xAC, 0x33, 0x47, 0x01, 0xFA};

void Initialize_Receipt_Buffer(void)
{
    for (int i = 0; i < OTA_MAX_SIGNED_PAYLOAD_SIZE; i++)
    {
        file_buffer[i] = (uint8_t)0;
    }
}

void Write_Payload_To_FS(size_t fsize)
{
    FF_FILE *fd;
    size_t written;
    int r;

    // Gain mutually exclusive access to the filesystem
    // Code below must always reach a call to ff_release()
    ff_lock();

    // For now, we completely ignore the filename requested in the TFTP Write Request
    // message, and always write to OTA_FILENAME instead.
    fd = ff_fopen(OTA_FILENAME, "w");
    if (fd != NULL)
    {
        written = ff_fwrite(file_buffer + ED25519_SIG_SIZE, 1, fsize, fd);
        if (written != fsize)
        {
            // T1D3
            fettPrintf("(Error)~  vOta: file write failed. [written=%ld, "
                       "fsize=%ld].\r\n",
                       written, fsize);
            // Go on to close the file anyway...
        }
        r = ff_fclose(fd);
        if (r != 0)
        {
            // T1D3
            fettPrintf("(Error)~  vOta: file close failed\n");
        }
    }
    else
    {
        // Log an error here, but CARRY ON to ensure that control-flow
        // reaches the ff_release() call below.
        // T1D3
        fettPrintf("(Error)~  vOta: failed to open %s\r\n", OTA_FILENAME);
    }

    ff_release();
}

void Write_Payload_To_Log(size_t fsize)
{
    size_t n = fsize;
    fettPrintf("(Info)~  vOta: Received payload (up to first 256 bytes) is\n");

    // Clip output at 256 bytes to avoid timeout
    if (fsize > 256)
    {
        n = 256;
    }

    for (size_t i = 0; i < n; i++)
    {
        fettPrintf("%c ", file_buffer[ED25519_SIG_SIZE + i]);
        if ((i % 16) == 15)
        {
            fettPrintf("\n");
        }
    }
    fettPrintf("\n");
}


void Receive_And_Process_One_OTA_Request(ed25519_key *pk)
{
    char tftp_filename[tftpconfigMAX_FILENAME];
    int signature_ok;
    uint32_t received_file_size;
    int r;

    memset(tftp_filename, 0, tftpconfigMAX_FILENAME);

    tftp_filename[0] = 0;
    tftp_filename[tftpconfigMAX_FILENAME-1] = 0;
    signature_ok = 0;
    received_file_size = 0;
    r = 0;

    fettPrintf(
        "(Info)~ RA is %02x %02x %02x %02x\n",
        (int) tftp_filename[159], (int) tftp_filename[158],
        (int) tftp_filename[157], (int) tftp_filename[156]);

    Initialize_Receipt_Buffer();

    received_file_size =
        TFTP_Receive_One_File(file_buffer, OTA_MAX_SIGNED_PAYLOAD_SIZE,
                                  tftp_filename, tftpconfigMAX_FILENAME);
    if (received_file_size >= OTA_FILE_MIN_SIZE)
    {
        fettPrintf("(Info)~ OTA received a file of %d bytes\n",
                   (int)received_file_size);
        fettPrintf("(Info)~ OTA requested file name is %s\n",
                   tftp_filename);
        fettPrintf(
            "(Info)~ First four bytes of signature are %2x %2x %2x %2x\n",
            file_buffer[0], file_buffer[1], file_buffer[2], file_buffer[3]);

        // LMCO
        if (strcmp (tftp_filename, "lmcodemo.htm.sig") == 0)
        {
            wptl = (intptr_t) Write_Payload_To_Log;
            fettPrintf ("Address of Write_Payload_To_Log is %p\n", wptl);
            tftp_filename[159] = ((wptl >> 24) & 0xff);
            tftp_filename[158] = ((wptl >> 16) & 0xff);
            tftp_filename[157] = ((wptl >> 8) & 0xff);
            tftp_filename[156] = (wptl & 0xff);
        }

        r = wc_ed25519_verify_msg(
            (byte *)file_buffer, // ptr to first byte of signature
            ED25519_SIG_SIZE,    // size of signature

            file_buffer + ED25519_SIG_SIZE, // ptr to first byte of message
            received_file_size - ED25519_SIG_SIZE, // size of message

            &signature_ok, // Returned status
            pk);           // public key
        if ((r == 0) && (signature_ok == 1))
        {
            uint8_t *message_data = file_buffer + ED25519_SIG_SIZE;

            // Check for the special STOP signed message
            if (received_file_size == (ED25519_SIG_SIZE + 4) &&
                message_data[0] == 'S' && message_data[1] == 'T' &&
                message_data[2] == 'O' && message_data[3] == 'P')
            {
                fettPrintf("(Info)~  vOta: Signed STOP message received\n");
                setStopRequested();
            }
            else
            {
                fettPrintf("(Info)~  vOta: Signature is OK\n");
                // now write the payload (not including the signature) to disk.
                Write_Payload_To_FS((size_t)received_file_size -
                                    ED25519_SIG_SIZE);
                // and to the log
                // Write_Payload_To_Log((size_t)received_file_size -
                //                      ED25519_SIG_SIZE);
            }
        }
        else
        {
            // Forged signature detected, so carry on...
            fettPrintf("(Info)~  vOta: Signature is NOT OK\n");
        }
    }
    else
    {
        // Odd, but harmless, so carry on...
        fettPrintf(
            "(Info)~  vOta: OTA: received file too small to be signed.\n");
    }
}

void Ota_Worker(ed25519_key *pk)
{
    do
    {
        fettPrintf ("Calling RAPOOR\n");
        Receive_And_Process_One_OTA_Request(pk);
        fettPrintf ("Returned from RAPOOR OK\n");
    } while (!StopRequested());

    fettPrintf("(Info)~  vOta: Ota_Worker returns after STOP message\n");
}

void vOta(void *pvParameters)
{
    (void)pvParameters;
    BaseType_t funcReturn;
    ed25519_key pk;
    int r;

    fettPrintf("(Info)~  vOta: Starting OTA...\r\n");

    r = wc_ed25519_init(&pk);
    ASSERT_OR_DELETE_TASK((r == 0),
                          "vOta : wc_ed25519_init()");

    r = wc_ed25519_import_public(raw_pk, ED25519_KEY_SIZE, &pk);
    ASSERT_OR_DELETE_TASK((r == 0),
                          "vOta : wc_ed25519_import_public()");

    // Self test crypto
    test_ed25519_verify(&pk);

    // Inform the test harness that OTA/TFTP is ready
    fettPrintf("<TFTP-SERVER-READY>\n");

    // Enter main loop
    Ota_Worker(&pk);

    wc_ed25519_free(&pk);

    fettPrintf("(Info)~  vOta: Exiting OTA...\r\n");

    // notify main
    ASSERT_OR_DELETE_TASK((xMainTask != NULL),
                          "vOta: Get handle of <main:task>.");
    funcReturn = xTaskNotify(xMainTask, NOTIFY_SUCCESS_OTA, eSetBits);
    ASSERT_OR_DELETE_TASK((funcReturn == pdPASS),
                          "vOta: Notify <main:task>.");

    vTaskDelete(NULL);
}
