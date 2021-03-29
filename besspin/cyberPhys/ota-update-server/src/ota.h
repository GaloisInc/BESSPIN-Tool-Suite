#ifndef __SRC_OTA_H
#define __SRC_OTA_H

#include <ctype.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/param.h>
#include <unistd.h>
#include <openssl/hmac.h>

// Secret key length
#define SECRET_KEY_LENGTH 64 // 512 bits
// Max filename length
#define MAX_FILENAME_LENGTH 64
#define SIGNATURE_LEN 64 // 512 bits
#define DEFAULT_RESPONSE_SIZE 128
// Saved filename
char ota_filename[MAX_FILENAME_LENGTH];
// Signature
char ota_signature[SIGNATURE_LEN];
// Secret key
char ota_secret_key[SECRET_KEY_LENGTH];

// State machine variables
int ota_filename_ok;
int ota_file_ok;

int load_secret_key(char *filepath);
void process_patch_filename(char *buffer, size_t len, char* response_buffer, size_t response_buffer_len);
void process_patch_file(char *buffer, size_t buf_len, int tcp_fd, size_t payload_len, char* response_buffer, size_t response_buffer_len);
void process_patch_signature(char *buffer, size_t len, char* response_buffer, size_t response_buffer_len);
void process_get(char *buffer, size_t buffer_len);

#endif
