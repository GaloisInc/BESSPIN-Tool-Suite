#include "./ota.h"
#include "./http.h"

// Filename prefix
const char* PREFIX = "/tmp/";
char response[DEFAULT_RESPONSE_SIZE];
size_t response_len;

int load_secret_key(char *filepath) {
    printf(">>> Loading secret key...\n");
    FILE *fp;
    uint8_t filebuf[SECRET_KEY_LENGTH*2];
    fp = fopen(filepath, "r");
    if (!fp)
    {
        printf(">>> Could not open file %s\n", filepath);
        return 1;
    }
    size_t bytes_read = 0;
    while (!feof(fp))
    {
        bytes_read = fread(filebuf, 1, SECRET_KEY_LENGTH*2, fp);
        if (bytes_read == SECRET_KEY_LENGTH*2)
        {
            break;
        }
    }

    for (uint8_t idx = 0; idx < SECRET_KEY_LENGTH; idx++) {
        char hex[] = {filebuf[idx*2],filebuf[idx*2+1]};
        int num = (int)strtol(hex, NULL, 16);
        ota_secret_key[idx] = (uint8_t)num;
    }
    printf(">> Key loaded!\n");
    return 0;
}


void process_patch_filename(char *buffer, size_t len, char* response_buffer, size_t response_buffer_len) {
    printf(">>> process_filename\n");
    char tmp[80];
    memset(tmp, 0xCC, 80); // so it is easier to see on stack
    memcpy(tmp, buffer, len);
    char response[DEFAULT_RESPONSE_SIZE];

    if(safe_strstr(tmp, ".elf", 64) == NULL && safe_strstr(tmp, ".bin", 64) == NULL &&
       safe_strstr(tmp, ".sh", 64) == NULL) {
       printf(">>> Bad filename. Only *.elf, *.bin, *.sh files are supported.\n");
       ota_filename_ok = 0;
       response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, "Bad filename. Only *.elf, *.bin, *.sh files are supported.");
    } else {
        memcpy(ota_filename, buffer, len);
        ota_filename[len] = 0;
        printf(">>> Filename: %s\n", ota_filename);
        ota_filename_ok = 1;
        response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, ota_filename);
    }
    printf(">>>process_filename done\n");
    snprintf(response_buffer, response_buffer_len,
                    "HTTP/1.1 200 Ok\r\n"
                    "Content-Length: %lu\r\n"
                    "\r\n"
                    "%s\r\n",
                    response_len+2, response);
}

void process_patch_file(char *buffer, size_t buf_len, int tcp_fd, size_t payload_len, char* response_buffer, size_t response_buffer_len) {
    printf(">>> process_file\n");
    char filename[MAX_FILENAME_LENGTH + strlen(PREFIX)]; // write all uploaded files to some location
    strcpy(filename, PREFIX);
    strncat(filename, ota_filename, MAX_FILENAME_LENGTH);
    printf(">>> Opening file %s\r\n",filename);
    FILE* fp = fopen(filename, "w");
    if (!fp)
    {
        printf("could not open file %s\n", filename);
        response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, "Could not open file %s", filename);
        snprintf(response_buffer, response_buffer_len,
                    "HTTP/1.1 200 Ok\r\n"
                    "Content-Length: %lu\r\n"
                    "\r\n"
                    "%s\r\n",
                    response_len+2, response);
        return;
    }
    // first, copy the buffer to the file
    int copy_len = MIN(payload_len, buf_len);
    fwrite(buffer, 1, copy_len, fp);
    int remaining_len = payload_len - copy_len;
    int file_error = 0;
    while (remaining_len > 0)
    {
        int bytes_read = read(tcp_fd, buffer, MIN(buf_len, remaining_len));
        if (bytes_read <= 0)
        {
            if (bytes_read < 0 && (errno == EAGAIN || errno == EWOULDBLOCK))
            {
                continue;
            }

            printf(">>> error reading remaining %d bytes from client\n", (int) payload_len);
            fclose(fp);
            ota_file_ok = 0;
            response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, "File error reading remaining %d bytes from client", (int) payload_len);
            file_error = 1;
            break;
        }
        else
        {
            fwrite(buffer, 1, bytes_read, fp);
            remaining_len = remaining_len - bytes_read;
        }
    }
    if (file_error == 0) {
        fclose(fp);
        ota_file_ok = 1;
        printf(">>> file (%d bytes) written successfully to %s\n", (int) payload_len, filename);
        response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, "File (%d bytes) written successfully to %s", (int) payload_len, filename);
    }
    snprintf(response_buffer, response_buffer_len,
                    "HTTP/1.1 200 Ok\r\n"
                    "Content-Length: %lu\r\n"
                    "\r\n"
                    "%s\r\n",
                    response_len+2, response);
}

void process_patch_signature(char *buffer, size_t len, char* response_buffer, size_t response_buffer_len) {
    printf(">>> process_signature\n");
    FILE *fp;
    uint8_t filebuf[1024];
    size_t bytes_read;
    // OpenSSL HMAC context
    HMAC_CTX *ctx;
    uint8_t *hmac;
    unsigned int hmac_len;

    if (strnlen(ota_filename, MAX_FILENAME_LENGTH) == 0 || strnlen(ota_filename, MAX_FILENAME_LENGTH) == MAX_FILENAME_LENGTH ||
        !(ota_file_ok && ota_filename_ok))
    {
        printf(">>> Invalid filename or file.\n");
        response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, "Invalid filename or file.");
        snprintf(response_buffer, response_buffer_len,
                    "HTTP/1.1 200 Ok\r\n"
                    "Content-Length: %lu\r\n"
                    "\r\n"
                    "%s\r\n",
                    response_len+2, response);
        return;
    }
    char filename[MAX_FILENAME_LENGTH + strlen(PREFIX)]; // read all uploaded files from some location
    strcpy(filename, PREFIX);
    strncat(filename, ota_filename, MAX_FILENAME_LENGTH);
    printf("opening file %s\n", filename);
    fp = fopen(filename, "r");
    if (!fp)
    {
        printf("could not open file %s\n", filename);
        response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, "Could not open file %s", filename);
        snprintf(response_buffer, response_buffer_len,
                    "HTTP/1.1 200 Ok\r\n"
                    "Content-Length: %lu\r\n"
                    "\r\n"
                    "%s\r\n",
                    response_len+2, response);
        return;
    }

    ctx = HMAC_CTX_new();
    HMAC_Init_ex(ctx, ota_secret_key, SECRET_KEY_LENGTH, EVP_sha256(), NULL);
    hmac = (uint8_t *) malloc(HMAC_size(ctx));

    while (!feof(fp))
    {
        bytes_read = fread(filebuf, 1, 1024, fp);
        if (bytes_read > 0)
        {
            HMAC_Update(ctx, &filebuf[0], bytes_read);
        }
    }

    HMAC_Final(ctx, hmac, &hmac_len);
    
    printf("HMAC computed for file %s:\n", filename);
    for (int i = 0; i < hmac_len; i++)
    {
        printf("%02X", hmac[i]);
    }
    printf("\n");

    memcpy(ota_signature, buffer, len);
        
    printf("Signature submitted:\n");
    for (int i = 0; i < len; i++) 
    {
        printf("%02X", (unsigned char) buffer[i]);
    }
    printf("\n");

    int result = memcmp(hmac, ota_signature, hmac_len); // if 0, signatures match

    HMAC_CTX_free(ctx);
    free(hmac);
    fclose(fp);

    char cmd[MAX_FILENAME_LENGTH + strlen(PREFIX)];
    if (result == 0) {
        printf(">>> Verification OK\n");
        response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, "Verification OK.");
        strcpy(cmd, "chmod +x ");
        strncat(cmd, filename, MAX_FILENAME_LENGTH-10);
        printf(">>> Executing command: %s\n",cmd);
        system(cmd);
        memset(cmd,0,strlen(cmd));
        strncat(cmd, filename, MAX_FILENAME_LENGTH-10);
        // Enable running in the backgroud
        strcat(cmd, " &"); // fixed string concatenation
        printf(">>> Executing command: %s\n",cmd);
        system(cmd);
        printf(">>> Program finished...\n");
    } else {
        printf(">>> Verification failed\n");
        response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, "Verification failed.");
        strcpy(cmd, "rm ");
        strncat(cmd, filename, MAX_FILENAME_LENGTH-4);
        printf(">>> Executing command: %s\n",cmd);
        system(cmd);
    }
    snprintf(response_buffer, response_buffer_len,
                "HTTP/1.1 200 Ok\r\n"
                "Content-Length: %lu\r\n"
                "\r\n"
                "%s\r\n",
                response_len+2, response);
}

void process_get(char *buffer, size_t buffer_len) {
    response_len = snprintf(response, DEFAULT_RESPONSE_SIZE, "OTA firmware update server v1.0");
    snprintf(buffer, buffer_len,
                "HTTP/1.1 200 Ok\r\n"
                "Content-Length: %lu\r\n"
                "\r\n"
                "%s\r\n",
                response_len+2, response);
}
