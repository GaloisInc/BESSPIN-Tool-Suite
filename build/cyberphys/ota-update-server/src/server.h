#ifndef __SERVER_H
#define __SERVER_H

#include <arpa/inet.h>
#include <errno.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <netinet/in.h>
#include <sys/poll.h>
#include <sys/socket.h>

#include "./connection.h"
#include "./fd.h"
#include "./safe_strstr.h"

/**
 * Custom configuration parameters.
 *
 * Check the Makefile at the root of the
 * repository to know more.
 */
#define HSTATIC_MAX_CLIENTS 10
#define HSTATIC_PORT 5050
#define HSTATIC_TCP_BACKLOG 4

/**
 * Encapsulates the properties of the server.
 */
typedef struct server
{
	// poll_list is the list of poll FDs
	struct pollfd poll_list[HSTATIC_MAX_CLIENTS + 1];

	// client_count is the number of currently-connected clients
	int client_count;

	// server connection that holds the underlying passive
	// socket where connections get accepted from.
	connection_t *conn;

    // client connections that are open
	connection_t *client_conn[HSTATIC_MAX_CLIENTS + 1];

	// callback to execute whenever a new connection
	// is accepted.
	connection_handler connection_handler;
} server_t;

/**
 * Destroys the instantiated server, freeing all of its
 * resources and closing and pending connections.
 */
int server_destroy(server_t *server);

/**
 * Instantiates a new server
 */
server_t *
server_create(connection_handler handler);

/**
 * Accepts connections and processes them using the handler specfied
 * in the server struct.
 */
int server_serve(server_t *server);

/**
 * Creates a socket for the server and makes it passive such that
 * we can wait for connections on it later.
 *
 * It uses `INADDR_ANY` (0.0.0.0) to bind to all the interfaces
 * available.
 *
 * The port is defined at compile time via the PORT definition.
 */
int server_listen(server_t *server);

#endif
