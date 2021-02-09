#include "./http.h"
#include "./ota.h"

const static char *http_response_no_content = "HTTP/1.1 204 No content\r\n"
                                            "Content-Length: 12\r\n"
                                            "\r\n"
                                            "No content\r\n";

static const char *buf = NULL;

static void loadString(const char *s)
{
    buf = s;
}

static long long int getNextNumber(void)
{
    /* 
     * Infinite list of todo items that will never happen here:
     * - Unicode support
     * - Error handling for non-integer inputs
     * - Integers that are too big, so have overflows/wraparounds
     */

    if (buf == NULL)
    {
        return 0;
    }

    char *endPtr = NULL;
    long long int result = strtoll(buf, &endPtr, 0); // overwrites endPtr

    if (endPtr == NULL)
    {
        buf = NULL;
    }
    else if (*endPtr == '/')
    {
        /*
         * This is the desired state: the first "invalid" character
         * is the slash character, so we'll start again next time one
         * character beyond it. 
         */
        buf = endPtr + 1;
    }
    else if (endPtr == buf)
    {
        /* No valid number found at all! Note absence of error handling. */
        buf = NULL;
        result = 0;
    }
    else
    {
        /* Probably at the 0-terminated end of the string, i.e, *endPtr = 0 */
        buf = endPtr;
    }

    return result;
}


int http_handler(connection_t *conn)
{
    int n = 0;
    memset(rx_buf,0,HTTP_BUFFER_LENGTH);
    memset(tx_buf,0,HTTP_BUFFER_LENGTH);

    for (;;)
    {
        n = read(conn->fd, rx_buf, HTTP_BUFFER_LENGTH);
        if (n == -1)
        {
            if (errno == EAGAIN || errno == EWOULDBLOCK)
            {
                break;
            }

            perror(">>> read\n");
            printf(">>> failed to read from the client\n");
            return -1;
        }
        else if (n == 0)
        {
            // not being able to read anything means the other side dropped
            return -1;
        }
        else
        {
            // n is > 0
            // process response
            http_parse_request(conn->fd, rx_buf, n);
        }
    }

    n = write(conn->fd, tx_buf, strlen(tx_buf));
    if (n == -1)
    {
        perror(">>> write");
        printf(">>> failed to write to client\n");
        return -1;
    }

    return 0;
}

enum {
    OTA_UNKNOWN,
    OTA_FILENAME,
    OTA_FILE,
    OTA_SIGNATURE,
};

void http_parse_request(int fd, char *buf, size_t len)
{
    int idx = 0;
    if (0 == strncmp("GET", &buf[idx], 3))
    {
        process_get(tx_buf, HTTP_BUFFER_LENGTH);
    }
    else if (0 == strncmp("PATCH", &buf[idx], 5))
    {
        idx = 6;
        int cmd = OTA_UNKNOWN;
        // could be "/&val/length" with body having the bytes
        if (0 == strncmp("/filename/", &buf[idx], 10))
        {
            idx += 10;
            cmd = OTA_FILENAME;
        }
        else if (0 == strncmp("/signature/", &buf[idx], 11))
        {
            idx += 11;
            cmd = OTA_SIGNATURE;
        }
        else if (0 == strncmp("/file/", &buf[idx], 6))
        {
            idx += 6;
            cmd = OTA_FILE;
        }
        else
        {
            printf(">>> Unknown value\n");
            return;
        }

        loadString(&buf[idx]);
        int requestLength = getNextNumber();

        // Parse the rest of the request - essentially we're just looking for a
        // blank line and passing the rest of the buffer along

        char *pch;
        pch = safe_strstr(buf, "\r\n\r\n", len); // CRLF after a CRLF

        if (pch == NULL) 
        {
            printf(">>> malformed request\n");
            return;
        }

        pch = pch + 4; // jump over the CRLFCRLF
        size_t bufferRemaining = len - (pch - buf);

        switch (cmd)
        {
        case OTA_FILENAME:
            process_patch_filename(pch, (size_t)requestLength, tx_buf, HTTP_BUFFER_LENGTH);
            break;
        case OTA_FILE:
            // here, we have to pass the file descriptor along because the data may be large
            process_patch_file(pch, bufferRemaining, fd, (size_t)requestLength, tx_buf, HTTP_BUFFER_LENGTH);
            break;
        case OTA_SIGNATURE:
            process_patch_signature(pch, (size_t)requestLength, tx_buf, HTTP_BUFFER_LENGTH);
            memset(ota_filename, 0, sizeof(ota_filename));
            memset(ota_signature, 0, sizeof(ota_signature));
            ota_filename_ok = 0;
            ota_file_ok = 0;
            break;
        default:
            printf(">>> Unknown command\n");
            break;
        }
    }
    else
    {
        printf(">>> Unknown command\n");
        strcpy(tx_buf, http_response_no_content);
    }
}
