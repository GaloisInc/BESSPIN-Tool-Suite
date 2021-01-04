/**
 * Infotainment Server
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

#ifndef __INFOTAINMENT_SERVER_H__
#define __INFOTAINMENT_SERVER_H__

#include "infotainment_defs.h"

#include <stdbool.h>
#include <stdint.h>

// initialize the server state
bool initialize(void);

// get the UDP socket, creating it if necessary
int udp_socket(void);

// the main event loop
int main_loop(void);

// stop the server (e.g., on a Ctrl-C)
void stop(void);

#endif // __INFOTAINMENT_SERVER_H__