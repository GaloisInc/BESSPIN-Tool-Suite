// This is the main function executed by fett -- It is just a wrapper

#include <stdio.h>

void main_fett (void);

//Define main apps + other tests
#if defined(FETT_HTTPS)
    extern void main_https (void);
#elif defined(FETT_OTA)
    extern void main_ota (void);
#endif

void main_fett () {

    printf ("\n>>>Beginning of Fett<<<\n");

    #if defined(FETT_HTTPS)
        main_https ();
    #elif defined(FETT_OTA)
        main_ota ();
    #endif

    printf ("\n>>>End of Fett<<<\n");
    return;
}
