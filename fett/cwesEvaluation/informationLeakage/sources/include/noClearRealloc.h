/* This is the common header for nonstandard-noClearRealloc tests */
#ifndef __NO_CLEAR_REALLOC_H__
#define __NO_CLEAR_REALLOC_H__

#include "nonstdCommon.h"

#define DELTA_SIZE_MIN MALLOC_BLOCK_SIZE_MIN/2

typedef enum reallocSize_ {SHRINK, EXPAND} reallocSize_t;

void noClearReallocTest(reallocSize_t option);

#endif