// This is the main task executed by ota

#include "fettFreeRTOS.h"
#include "ota_common.h"
#include "ota_tests.h"
#include "tftp_server.h"

// The maximum size of a file that can be received to the in-memory buffer
#define TFTP_FILE_BUFFER_LEN 65536

#define OTA_FILE_MIN_SIZE (ED25519_SIG_SIZE + 1)

uint8_t file_buffer[TFTP_FILE_BUFFER_LEN];
char    filename_buffer[ffconfigMAX_FILENAME];

void vOta (void *pvParameters);
void Ota_Worker (void);
void Write_Payload (size_t fsize);
void Initialize_Receipt_Buffers (void);

void Initialize_Receipt_Buffers (void)
{
  for (int i = 0; i < TFTP_FILE_BUFFER_LEN; i++)
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
      fettPrintf ("(Info)~  vOta: file open/create failed\n");
      return;
    }
  written = ff_fwrite (file_buffer, 1, fsize, fd);
  if (written != fsize)
    {
      fettPrintf ("(Info)~  vOta: file write failed\n");
      // Go on to close the file anyway...
    }
  r = ff_fclose (fd);
  if (r != 0)
    {
      fettPrintf ("(Info)~  vOta: file close failed\n");
    }
}

void Ota_Worker (void)
{
  ed25519_key pk;
  int r;

  r = wc_ed25519_init (&pk);
  if (r != 0)
    {
      fettPrintf ("(Info)~  vOta: wc_ed25519_init() failed\n");
      return;
    }

  r = wc_ed25519_import_public (raw_pk, ED25519_KEY_SIZE, &pk);
  if (r != 0)
    {
      fettPrintf ("(Info)~  vOta: wc_ed25519_import_public() failed\n");
      return;
    }


  // Normally, this would loop forever, but for initial testing,
  // we'll just receive and process one file before returning
  // for (;;)
  {
    int      signature_ok;
    uint32_t received_file_size;
  
    Initialize_Receipt_Buffers();
    
    received_file_size = TFTP_Receive_One_File (file_buffer,
                                                TFTP_FILE_BUFFER_LEN,
                                                filename_buffer,
                                                ffconfigMAX_FILENAME);
    if (received_file_size >= OTA_FILE_MIN_SIZE)
      {
        r = wc_ed25519_verify_msg((byte *) file_buffer,  // ptr to first byte of signature
                                  ED25519_SIG_SIZE,   // size of signature
                                  
                                  file_buffer + ED25519_SIG_SIZE,     // ptr to first byte of message
                                  received_file_size - ED25519_SIG_SIZE, // size of message
                                  
                                  &signature_ok,            // Returned status
                                  &pk);                     // public key

        if (signature_ok == 1)
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
        fettPrintf ("(Info)~  vOta: OTA: received file too small to be signed.\n");
      }

  }

}



void vOta (void *pvParameters) {
    (void) pvParameters;
    BaseType_t funcReturn;

    fettPrintf("(Info)~  vOta: Starting OTA...\r\n");

    test_ed25519_verify();

    Ota_Worker();
    
    fettPrintf("(Info)~  vOta: Exitting OTA...\r\n");

    //notify main
    vERROR_IF_EQ(xMainTask, NULL, "vOta: Get handle of <main:task>.");
    funcReturn = xTaskNotify( xMainTask, NOTIFY_SUCCESS_OTA ,eSetBits);
    vERROR_IF_NEQ(funcReturn, pdPASS, "vOta: Notify <main:task>.");

    vTaskDelete (NULL);
}
