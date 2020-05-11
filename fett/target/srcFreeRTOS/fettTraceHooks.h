/*
- This file has the definitions of trace hooks as defined in https://www.freertos.org/rtos-trace-macros.html
- These hooks are activated only if `fett.py` is executed with the `-d` flag
*/

extern void hook_TaskCreateSuccess (void * xTask);
extern void hook_TaskSwitchedIn (void * xTask);

#define traceTASK_CREATE(xTask) hook_TaskCreateSuccess(xTask)
//#define traceTASK_SWITCHED_IN() hook_TaskSwitchedIn(pxCurrentTCB)

