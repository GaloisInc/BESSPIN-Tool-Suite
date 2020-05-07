#include <stdint.h>

// Waits for an incoming connection on TFTP_PORT and receives
// a file, writing the contents to buffer[0 .. buffer_len-1] and
// the indicated file name into file_name[0 .. file_name_len-1].
// file_name will be zero-terminated.
//
// Returns the number of bytes received on success.
// Returns 0 on error.
uint32_t TFTP_Receive_One_File (uint8_t *buffer,         // out
                                uint32_t buffer_len,     // in
                                char    *file_name,      // out
                                uint32_t file_name_len); // in
