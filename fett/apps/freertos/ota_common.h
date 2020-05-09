#include "fettFreeRTOS.h"

// The known public key used for signature verification.
// Completed in ota_common.c
extern const byte raw_pk[ED25519_KEY_SIZE];

// The incoming TFTP file buffer and file name. Completed in ota.c
extern uint8_t file_buffer[OTA_MAX_SIGNED_PAYLOAD_SIZE]; // SIZE set in setupEnv.json
extern char    filename_buffer[ffconfigMAX_FILENAME];
