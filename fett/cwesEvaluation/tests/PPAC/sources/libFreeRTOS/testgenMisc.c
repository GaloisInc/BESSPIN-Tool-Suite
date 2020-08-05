/*
Functions used for Misc implementation on FreeRTOS
*/

#include "testgenFreeRTOS.h"

static uint8_t doEndTest = 0;
MessageBufferHandle_t globalMsgBuffer = NULL;

// Only printf while "ON"
void onPrintf (const char * textToPrint, ...) {
    if (!doEndTest) {
        va_list args;
        va_start(args, textToPrint);
        vprintf(textToPrint, args);
        va_end(args);
    }
    return;
}

//turn off printing. and print >>>EndofTestgen<<<
void exitTest (uint8_t exitCode) {
    if (!doEndTest) {
        doEndTest = 1;
        printf ("EXIT: exiting testgen with code <%x>\n",exitCode);
        printf ("\n>>>End of Testgen<<<\n");
    }
    return;
}

/*fake function because sometimes, a wolfssl functions calls it despite defining NO_FILESYSTEM. 
In such a case, such culprit function should have a wrapper and the functionality implemented here */
void _open (const char * dump1, int dump2, ...) {
    (void) (dump1);
    (void) (dump2);
    onPrintf ("FATAL ERROR: <_open> should never be called.\n");
    prEXIT(1);
}

/* Fake functions because time is needed for certificated expiry and beginning dates.
_gettimeofday appears to be called from time.h; also the XTIME function overrides the calls to time().
   This can be improved by being called to set at time of boot and then adding 
   the tickCount (with an interrupt at tickCount overflow).
   It does not seem worth it to spend the time and do that for testgen purposes */
void _gettimeofday (struct timeval *__p, void *__tz) {
    if (__tz != NULL) {
        onPrintf("Warning: timezone pointer is not NULL in custom <gettimeofday>.\n");
    }
    //this is only temporary ---- will be changed!!
    if (__p == NULL) {
        onPrintf ("<INVALID> No timeval allocated in <gettimeofday>.\n");
        prEXIT(1);
    }
    #ifdef FAKETIMEOFDAY
        __p->tv_sec = FAKETIMEOFDAY;
    #else
        onPrintf ("<INVALID> [gettimeofday]: FAKETIMEOFDAY is not defined!\n");
        prEXIT(1);
    #endif
    __p->tv_usec = 0UL;
    return;
}

time_t XTIME(time_t *t) {
    (void) t;
    #ifdef FAKETIMEOFDAY
        return FAKETIMEOFDAY;
    #else
        onPrintf ("<INVALID> [XTIME]: FAKETIMEOFDAY is not defined!\n");
        exitTest(2);
        return 0;
    #endif
}

/* Added as there is no such function in FreeRTOS. */
// type is not type anymore; it is the old size.
void *XREALLOC(void *p, size_t n, void* heap, int type)
{
    // This part is clean
    if (n == 0)
    {
       vPortFree (p);
       return NULL;
    }
    else if (p == NULL)
    {
       return pvPortMalloc (n);
    }

    //This has the dangerous part
    #if __riscv_xlen == 64
        unsigned int isItCustomCall = (heap != NULL) && ((intptr_t) heap == USE_TESTGEN_REALLOC);
    #else
        unsigned int isItCustomCall = (heap != NULL) && ((int) heap == USE_TESTGEN_REALLOC);
    #endif

    if (isItCustomCall == 0) { //super dangerous method
        onPrintf ("Warning: XREALLOC <dangerously defined> is used.\n");
    } 

    void *pvReturn = pvPortMalloc (n);
    if (pvReturn == NULL) {
        onPrintf ("<INVALID> [XREALLOC]: Failed to malloc.");
        exitTest (2); //cannot use prEXIT because this function is non-void
        return NULL;
    }

    if (isItCustomCall == 0) { //super dangerous method
        memcpy (pvReturn, p, n); //This is dangerous because n might be > size(p) and may be in a bad memory region.
    } else { //the custom safe call
        memcpy (pvReturn, p, (size_t) type); 
    }

    vPortFree (p);
    return pvReturn;
}

/* Added as no /dev/urandom to give the seed for RNG -- Not for REAL APPLICATIONS */
static uint8_t iSeed = 0; //start with the first one
int testgen_wc_GenerateSeed(uint8_t* seed, uint8_t sz) {
    uint8_t seedsArray [TESTGEN_WC_SEEDS_LEN] = { TESTGEN_WC_SEEDS };
    uint8_t seedOS = seedsArray[iSeed];
    memcpy (seed, &seedOS, sz); 
    iSeed++; //next time, use next seed
    if (iSeed >= TESTGEN_WC_SEEDS_LEN) {
        iSeed = 0;
    }
    return 0;
}

/*
--- This function is called by FreeRTOS_TCP_IP.c. This is a dirty implementation
 * Callback that provides the inputs necessary to generate a randomized TCP
 * Initial Sequence Number per RFC 6528.  THIS IS ONLY A DUMMY IMPLEMENTATION
 * THAT RETURNS A PSEUDO RANDOM NUMBER SO IS NOT INTENDED FOR USE IN PRODUCTION
 * SYSTEMS.
 */
uint32_t ulApplicationGetNextSequenceNumber(uint32_t ulSourceAddress,
                                            uint16_t usSourcePort,
                                            uint32_t ulDestinationAddress,
                                            uint16_t usDestinationPort)
{
    (void)ulSourceAddress;
    (void)usSourcePort;
    (void)ulDestinationAddress;
    (void)usDestinationPort;

    return uxRand();
}

/* This function sends some data to the message buffer */
uint8_t sendToMsgBuffer (void * xData, size_t xDataSize) {
    if (globalMsgBuffer == NULL) { //it was not created 
        size_t msgBufSize;
        #ifdef MSGBUF_SIZE
            msgBufSize = MSGBUF_SIZE;
        #else
            onPrintf ("WARNING: <MSGBUF_SIZE> is not defined. Using 32 by default.\n");
            msgBufSize = 32;
        #endif

        globalMsgBuffer = xMessageBufferCreate (msgBufSize);
        if (globalMsgBuffer == NULL) {
            onPrintf ("[sendToMsgBuffer]: Failed to create the global message buffer.\n");
            return uFALSE;
        }
    } //if it was not created

    size_t xBytesSent = xMessageBufferSend( globalMsgBuffer, xData, xDataSize, 0);
    if (xBytesSent != xDataSize) {
        onPrintf ("[sendToMsgBuffer]: Failed to send to the message buffer. [ret=%d]\n",xBytesSent);
        return uFALSE;
    }
    
    return uTRUE;
}

/* This function receives some data from the message buffer */
size_t recvFromMsgBuffer (void * xBuf, size_t xBufSize) {
    if (globalMsgBuffer == NULL) { //it was not created or received
        onPrintf ("[recvFromMsgBuffer]: There is no message buffer to receive from.\n");
        return 0;
    }

    return xMessageBufferReceive( globalMsgBuffer, xBuf, xBufSize, 0); //No waiting; not used in flow control to be more generic
}