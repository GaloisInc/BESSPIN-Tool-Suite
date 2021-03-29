/*
- This file is included in the used FreeRTOSConfig.h
*/

/* FF Filesystem requires thread local storage to
   store current working dir for each task */
#define configNUM_THREAD_LOCAL_STORAGE_POINTERS 4
