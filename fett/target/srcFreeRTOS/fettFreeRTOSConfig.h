/*
- This file is included in the used FreeRTOSConfig.h
*/

/* FF Filesystem requires thread local storage to
   store current working dir for each task */
#define configNUM_THREAD_LOCAL_STORAGE_POINTERS 4

// The baud rate of the UART set here, and the receiving end in the
// FireSim infrastucture must match.
//
// Initially, we had the baud rate a 3686400, based on a core clock
// rate of 100MHz, but that proved to be unreliable.
//
// This was investigated in CloudGFE Issue #101, and we decided to
// drop the baud rate to 115200.
//
// The SiFive UART specifications say that the divisor set here
// must be one less than the core clock rate divided by the required
// baud rate, rounded to the nearest integer, so
//  Divisor = int(100_000_000 / 115200) - 1
//          = int(868.055) - 1
//          = 867
//
// It is defined here, so it can be changed without modification
// of the FreeRTOS submodule
#define fettSIFIVE_UART_BAUD_RATE_DIVISOR 867
