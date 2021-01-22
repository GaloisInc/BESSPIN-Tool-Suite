/**
 * Infotainment Server
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

#include <signal.h>
#include "infotainment_server.h"
#include "infotainment_debug.h"
#include "infotainment_utils.h"

void interrupt_handler(int unused) {
    debug("interrupt received\n");
    stop();
}

// currently, the main function just runs the event loop
int main(int argc, char** argv) {
    // interrupt handling
    struct sigaction action;
    action.sa_handler = interrupt_handler;
    action.sa_flags = 0;
    sigemptyset(&action.sa_mask);
    sigaction(SIGINT, &action, NULL);

    debug("infotainment server starting\n");

    if (argc == 2) {
        // one argument means an override of the broadcast address
        set_broadcast_address(argv[1]);
    }

    int result;

    if (initialize()) {
        result = main_loop();
    } else {
        error("unable to initialize server\n");
    }

    if (result == 0) {
        debug("infotainment server exiting\n");
    } else
    {
        debug("infotainment server reported error %d\n", result);
    }
    
    return result;
}