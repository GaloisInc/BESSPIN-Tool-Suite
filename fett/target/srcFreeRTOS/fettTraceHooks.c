/*
- This file has the implementations of trace hooks declared in fettTraceHooks.h
- These hooks are activated only if `fett.py` is executed with the `-d` flag
*/

#include "fettFreeRTOS.h"

void hook_TaskSwitchedIn (void * xTask) {
    #if (FETT_DEBUG == 1) //to save cycles
        debugFettPrintf ("hook_TaskSwitchedIn: Switching in to task <%s>\r\n",pcTaskGetName(xTask));
    #else
        (void) xTask;
    #endif
    return;
}

void hook_TaskCreateSuccess (void * xTask) {
    #if (FETT_DEBUG == 1) //to save cycles
        debugFettPrintf ("hook_TaskCreate: Task <%s> is successfully created with priority=<%d>.\r\n",pcTaskGetName(xTask),uxTaskPriorityGet(xTask));
    #else
        (void) xTask;
    #endif
    return;
}
