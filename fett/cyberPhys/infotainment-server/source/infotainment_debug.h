/**
 * Infotainment Server Debug Functions
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 */

#ifndef __INFOTAINMENT_DEBUG_H__
#define __INFOTAINMENT_DEBUG_H__

#include <stdio.h>
#include <stdlib.h>

// basic debug and error output functions
#define error(args...) { fprintf(stderr, ##args); exit(1); }
#define debug(args...) { fprintf(stderr, ##args); }

#endif // __INFOTAINMENT_DEBUG_H__