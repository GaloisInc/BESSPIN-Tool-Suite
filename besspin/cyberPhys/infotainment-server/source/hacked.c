/**
 * Hacked Infotainment Server
 * Copyright (C) 2020-21 Galois, Inc.
 * @author Daniel M. Zimmerman <dmz@galois.com>
 * @refine besspin_cyberphys.lando
 */

#include <signal.h>
#include "hacked_server.h"
#include "hacked_utils.h"
#include "infotainment_debug.h" // no need to hack debug functions

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

    message("attempting to kill legitimate infotainment server\n");
    int result = system("systemctl stop infotainment-server.service");
    
    if (result != 0) {
        message("could not kill legitimate infotainmment server, running anyway. Result was %i\n",result);
    } else {
        message("legitimate infotainment server killed\n");
    }

    message("hacked infotainment server starting\n");

    #ifdef HACKED_POSITION_ADDRESS
    set_position_source(HACKED_POSITION_ADDRESS);
    #endif
    
    if (initialize()) {
        result = main_loop();
    } else {
        error("unable to initialize server\n");
    }

    if (result == 0) {
        message("hacked infotainment server exiting\n");
    } else
    {
        message("hacked infotainment server reported error %d\n", result);
    }
    
    return result;
}