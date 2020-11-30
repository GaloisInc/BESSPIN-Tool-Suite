#include "./server.h"

server_t *
server_create(connection_handler handler)
{
	server_t *server;
	connection_t *conn;

	if (handler == NULL)
	{
		printf("handler must be specified\n");
		return NULL;
	}

	conn = connection_create(CONNECTION_TYPE_SERVER);
	if (conn == NULL)
	{
		printf("failed to create server connection\n");
		return NULL;
	}

	server = malloc(sizeof(*server));
	if (server == NULL)
	{
		perror("malloc");
		printf("failed to allocate memory for server struct\n");
		return NULL;
	}

	server->client_count = 0;
	server->conn = conn;
	server->connection_handler = handler;

	for (int i = 0; i < HSTATIC_MAX_CLIENTS; i++)
	{
		server->poll_list[i].fd = -1;
	}

	return server;
}

int server_destroy(server_t *server)
{
	int err = 0;

	if (server->conn != NULL)
	{
		err = connection_destroy(server->conn);
		if (err)
		{
			printf("failed to destroy server connection\n");
			return err;
		}

		free(server->conn);

		server->conn = NULL;
	}

	server->poll_list[0].fd = -1;
	server->client_count = 0;

	return 0;
}

/**
 * Accepts all incoming established TCP connections
 * until a blocking `accept(2)` would occur.
 */
int _accept_all(server_t *server)
{
	struct sockaddr in_addr;
	socklen_t in_len = sizeof in_addr;
	connection_t *conn;
	int in_fd;

	// accept a connection if we have space to store it
	while (server->client_count < HSTATIC_MAX_CLIENTS)
	{
		in_fd = accept(server->conn->fd, &in_addr, &in_len);
		if (in_fd == -1)
		{
			if ((errno == EAGAIN) || (errno == EWOULDBLOCK))
			{
				return 0;
			}

			perror("accept");
			printf("failed unexpectedly while accepting "
				   "connection");
			return -1;
		}

		// Make the incoming socket non-blocking
		fd_make_nonblocking(in_fd);

		conn = connection_create(CONNECTION_TYPE_CLIENT);
		if (conn == NULL)
		{
			printf("failed to create connection struct\n");
			return -1;
		}

		conn->fd = in_fd;

		// add the connection to the connection set and poll list
		int i = 1;
		while (i <= HSTATIC_MAX_CLIENTS)
		{
			// we have to have _somewhere_ to store it
			if (server->poll_list[i].fd == -1)
			{
				printf("accepted connection from client #%d\n", i);
				server->client_conn[i] = conn;
				server->poll_list[i].fd = conn->fd;
				server->poll_list[i].events = POLLIN;
				server->client_count++;
				i = HSTATIC_MAX_CLIENTS + 1; 
			}
			else
			{
				i++;
			}
		}
	}

	return 0;
}

int server_serve(server_t *server)
{
	int err = 0;

	server->poll_list[0].fd = server->conn->fd;
	server->poll_list[0].events = POLLIN;


	for (;;)
	{
		// polling all our file descriptors

		int retval = poll(server->poll_list, HSTATIC_MAX_CLIENTS + 1, -1);
		if (retval > 0)
		{
			if (server->poll_list[0].revents & POLLIN)
			{
				err = _accept_all(server);
				if (err)
				{
					printf("failed to accept "
						   "connection\n");
					return err;
				}
			}

			for (int i = 1; i <= HSTATIC_MAX_CLIENTS; i++) 
			{
				if (server->poll_list[i].revents == POLLIN)
				{
					if (server->connection_handler(server->client_conn[i]) < 0)
					{
						printf("client #%d disconnected\n", i);
						err = connection_destroy(server->client_conn[i]);
						server->client_conn[i] = NULL;
						server->poll_list[i].fd = -1;
						server->client_count--;
						if (err)
						{
							printf("failed to destroy connection\n");
							return -1;
						}
						continue;
					}
				}
				else if (server->poll_list[i].revents > 0) // any other event is an error
				{
					printf("disconnecting client #%d\n", i);
					err = connection_destroy(server->client_conn[i]);
				    server->client_conn[i] = NULL;
					server->poll_list[i].fd = -1;
					server->client_count--;
					if (err) 
					{
						printf("failed to destroy connection\n");
						return -1;
					}
			 	}
			}
		}
		if (retval == -1)
		{
			if (errno == EINTR)
			{
				return 0;
			}

			perror("poll");
			printf("failed to poll for events");
			return -1;
		}
	}

	return 0;
}

int server_listen(server_t *server)
{
	int err = 0;
	struct sockaddr_in server_addr = {0};

	// `sockaddr_in` provides ways of representing a full address
	// composed of an IP address and a port.
	//
	// SIN_FAMILY   address family          AF_INET refers to the
	//                                      address family related to
	//                                      internet addresses
	//
	// S_ADDR       address (ip) in network byte order (big endian)
	// SIN_PORT     port in network byte order (big endian)
	server_addr.sin_family = AF_INET;
	server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	server_addr.sin_port = htons(HSTATIC_PORT);

	// The `socket(2)` syscall creates an endpoint for communication
	// and returns a file descriptor that refers to that endpoint.
	//
	// It takes three arguments (the last being just to provide
	// greater specificity):
	// -    domain (communication domain)
	//      AF_INET              IPv4 Internet protocols
	//
	// -    type (communication semantics)
	//      SOCK_STREAM          Provides sequenced, reliable,
	//                           two-way, connection-based byte
	//                           streams.
	err = (server->conn->fd = socket(AF_INET, SOCK_STREAM, 0));
	if (err == -1)
	{
		perror("socket");
		printf("Failed to create socket endpoint\n");
		return err;
	}

	// bind() assigns the address specified to the socket referred
	// to by the file descriptor (`listen_fd`).
	//
	// Here we cast `sockaddr_in` to `sockaddr` and specify the
	// length such that `bind` can pick the values from the
	// right offsets when interpreting the structure pointed to.
	err = bind(server->conn->fd,
			   (struct sockaddr *)&server_addr,
			   sizeof(server_addr));
	if (err == -1)
	{
		perror("bind");
		printf("Failed to bind socket to address\n");
		return err;
	}

	// Makes the server socket non-blocking such that calls that
	// would block return a -1 with EAGAIN or EWOULDBLOCK and
	// return immediately.
	err = fd_make_nonblocking(server->conn->fd);
	if (err)
	{
		printf("failed to make server socket nonblocking\n");
		return err;
	}

	// listen() marks the socket referred to by sockfd as a
	// passive socket, that is, as a socket that will be used to accept
	// incoming connection requests using accept(2).
	err = listen(server->conn->fd, HSTATIC_TCP_BACKLOG);
	if (err == -1)
	{
		perror("listen");
		printf("Failed to put socket in passive mode\n");
		return err;
	}

	return 0;
}
