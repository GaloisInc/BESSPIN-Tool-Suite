/**
 * Infotainment Server Debug Functions
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 */

#ifndef __INFOTAINMENT_DEBUG_H__
#define __INFOTAINMENT_DEBUG_H__

#include <stdio.h>
#include <stdlib.h>

#ifndef INFOTAINMENT_DEBUG_FLAG
#define INFOTAINMENT_DEBUG_FLAG 0
#endif

#ifndef INFOTAINMENT_INFO_FLAG
#define INFOTAINMENT_INFO_FLAG 0
#endif

// basic debug and error output functions
/**
 * An error. Prints and then exits the program.
 */
#define error(args...) { fprintf(stderr, ##args); exit(1); }

/**
 * A message. Prints unconditionally.
 */
#define message(args...) { if (INFOTAINMENT_INFO_FLAG) { fprintf(stderr, ##args); } }

/**
 * A debug message. Only prints if DEBUG_FLAG is 1.
 */
#define debug(args...) { if (INFOTAINMENT_DEBUG_FLAG) { fprintf(stderr, ##args); } }

#endif // __INFOTAINMENT_DEBUG_H__