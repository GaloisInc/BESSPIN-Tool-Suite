// This is the main task executed by ota

#include "fettFreeRTOS.h"
#include "ota_common.h"
#include "ota_tests.h"
#include "tftp_server.h"

#define OTA_FILE_MIN_SIZE (ED25519_SIG_SIZE + 1)

uint8_t file_buffer[OTA_MAX_SIGNED_PAYLOAD_SIZE]; // SIZE set in setupEnv.json
char    filename_buffer[ffconfigMAX_FILENAME];

void vOta (void *pvParameters);
void Ota_Worker (ed25519_key *pk);
void Write_Payload (size_t fsize);
void Initialize_Receipt_Buffers (void);


// This is the Public Key used for Ed25519 signature verification
static const byte raw_pk[ED25519_KEY_SIZE] =
  {0xBA, 0xFB, 0xD4, 0xBB, 0x9F, 0x8E, 0xCE, 0xC1,
   0xEC, 0xE7, 0x42, 0xD7, 0xEA, 0x3B, 0x2E, 0xE2,
   0xE0, 0x16, 0xE3, 0x0F, 0x27, 0x0B, 0xAE, 0x74,
   0xB3, 0x0B, 0xED, 0xAC, 0x33, 0x47, 0x01, 0xFA};


void Initialize_Receipt_Buffers (void)
{
  for (int i = 0; i < OTA_MAX_SIGNED_PAYLOAD_SIZE; i++)
    {
      file_buffer[i] = (uint8_t) 0;
    }
  for (int j = 0; j < ffconfigMAX_FILENAME; j++)
    {
      filename_buffer[j] = '\0';
    }
}


void Write_Payload (size_t fsize)
{
  FF_FILE *fd;
  size_t  written;
  int     r;

  fd = ff_fopen (filename_buffer, "w");
  if (fd == NULL)
    {
      fettPrintf ("(Error)~  vOta: file open/create failed\n");
      return;
    }
  written = ff_fwrite (file_buffer, 1, fsize, fd);
  if (written != fsize)
    {
      fettPrintf ("(Error)~  vOta: file write failed\n");
      // Go on to close the file anyway...
    }
  r = ff_fclose (fd);
  if (r != 0)
    {
      fettPrintf ("(Error)~  vOta: file close failed\n");
    }
}

void Ota_Worker (ed25519_key *pk)
{
  // Normally, this would loop forever, but for initial testing,
  // we'll just receive and process one file before returning
  // for (;;)
  {
    int      signature_ok;
    uint32_t received_file_size;
    int      r;
    
    Initialize_Receipt_Buffers();
    
    received_file_size = TFTP_Receive_One_File (file_buffer,
                                                OTA_MAX_SIGNED_PAYLOAD_SIZE,
                                                filename_buffer,
                                                ffconfigMAX_FILENAME);
    if (received_file_size >= OTA_FILE_MIN_SIZE)
      {
        fettPrintf ("(Info)~ OTA received a file of %d bytes\n", (int) received_file_size);
        fettPrintf ("(Info)~ OTA requested file name is %s\n", filename_buffer);
        fettPrintf ("(Info)~ First four bytes of signature are %2x %2x %2x %2x\n",
                    file_buffer[0],
                    file_buffer[1],
                    file_buffer[2], 
                    file_buffer[3]);
        
        r = wc_ed25519_verify_msg((byte *) file_buffer,  // ptr to first byte of signature
                                  ED25519_SIG_SIZE,   // size of signature
                                  
                                  file_buffer + ED25519_SIG_SIZE,     // ptr to first byte of message
                                  received_file_size - ED25519_SIG_SIZE, // size of message
                                  
                                  &signature_ok,            // Returned status
                                  pk);                      // public key
        if ((r == 0) && (signature_ok == 1))
          {
            fettPrintf ("(Info)~  vOta: Signature is OK\n");
            // now write the payload (not including the signature) to disk.
            Write_Payload ((size_t) received_file_size - ED25519_SIG_SIZE);
          } 
        else
          {
            fettPrintf ("(Info)~  vOta: Signature is NOT OK\n");
          }
        
      }
    else
      {
        fettPrintf ("(Error)~  vOta: OTA: received file too small to be signed.\n");
      }

  }

}



void vOta (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;
    ed25519_key pk;
    int r;

    fettPrintf("(Info)~  vOta: Starting OTA...\r\n");

    r = wc_ed25519_init (&pk);
    if (r != 0)
      {
        fettPrintf ("(Error)~  vOta: wc_ed25519_init() failed\n");
        return;
      }

    r = wc_ed25519_import_public (raw_pk, ED25519_KEY_SIZE, &pk);
    if (r != 0)
      {
        fettPrintf ("(Error)~  vOta: wc_ed25519_import_public() failed\n");
        return;
      }

    // Self test crypto
    test_ed25519_verify(&pk);

    // Inform the test harness that OTA/TFTP is ready
    fettPrintf ("<TFTP-SERVER-READY>\n");

    // Enter main loop
    Ota_Worker(&pk);
    
    wc_ed25519_free (&pk);

    fettPrintf("(Info)~  vOta: Exitting OTA...\r\n");

    //notify main
    vERROR_IF_EQ(xMainTask, NULL, "vOta: Get handle of <main:task>.");
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS_OTA ,eSetBits);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vOta: Notify <main:task>.");

    vTaskDelete (NULL);
}
