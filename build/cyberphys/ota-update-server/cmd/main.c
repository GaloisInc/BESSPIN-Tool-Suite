#include "../src/http.h"
#include "../src/server.h"
#include "../src/ota.h"

#include <signal.h>

server_t *server;

void sig_handler(int signo __attribute__((unused)))
{
    int err;

    if (server == NULL)
    {
        exit(0);
    }

    err = server_destroy(server);
    if (err)
    {
        printf("errored while gracefully destroying server\n");
        exit(err);
    }
}

/**
 * Main server routine.
 *
 *      -       instantiates a new server structure that holds the
 *              properties of our server;
 *      -       creates a socket and makes it passive with
 *              `server_listen`;
 *      -       accepts new connections on the server socket.
 *
 */
int main(int argc, char **argv)
{
    int err = 0;
    if (argc != 2) {
        perror("arguments");
        printf("Incorrect number of arguments, got %i, expected 2\n", argc);
        printf("Correct use: ./program path-to-key\n");
        return 1;
    }

    if (signal(SIGINT, sig_handler) == SIG_ERR ||
        signal(SIGTERM, sig_handler) == SIG_ERR)
    {
        perror("signal");
        printf("failed to install termination signal handler\n");
        return 1;
    }

    if (load_secret_key(argv[1])) {
        printf("failed to load secret key\n");
        return 1;
    }
    // Initialize variables
    ota_filename_ok = 0;
    ota_file_ok = 0;

    server = server_create(&http_handler);
    if (server == NULL)
    {
        printf("failed to instantiate server\n");
        return 1;
    }

    err = server_listen(server);
    if (err)
    {
        printf("Failed to listen on address :5050\n");
        return err;
    }

    printf("Server starting up.\n");
    err = server_serve(server);
    if (err)
    {
        printf("Failed serving\n");
        return err;
    }

    err = server_destroy(server);
    if (err)
    {
        printf("failed to destroy server\n");
        return 1;
    }

    free(server);
    server = NULL;

    return 0;
}
