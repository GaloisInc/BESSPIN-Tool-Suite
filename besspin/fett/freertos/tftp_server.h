#include <stdint.h>

#define DUMMY_TFTP 0

#define tftpconfigMAX_FILENAME  129

// IF DUMMY_TFTP == 1
//
//  Places a known, constant signed payload into buffer[0 .. 69]
//  Places "f" into file_name[0 .. 1]
//  Suitable as a dumb known-answer test, needing no TFTP client
//
// ELSE
//
//  Waits for an incoming connection on TFTP_PORT and receives
//  a file, writing the contents to buffer[0 .. buffer_len-1] and
//  the indicated file name into file_name[0 .. file_name_len-1].
//  file_name will be zero-terminated.
//
//  Returns the number of bytes received on success.
//  Returns 0 on error.
uint32_t TFTP_Receive_One_File (uint8_t *buffer,         // out
                                uint32_t buffer_len,     // in
                                char    *file_name,      // out
                                uint32_t file_name_len); // in
