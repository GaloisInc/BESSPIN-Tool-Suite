/**
 * Infotainment Server Utility Functions
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

#include <unistd.h>

#include "infotainment_defs.h"

// get a UDP socket listening on port, creating it if necessary
int udp_socket(int port);

// get a character (x, y, z) based on the CAN ID for a position dimension
char char_for_dimension(canid_t dimension_id);

// get a pointer to the position (in the state) based on the CAN ID for a position dimension
float *position_for_dimension(infotainment_state the_state, canid_t dimension_id);
