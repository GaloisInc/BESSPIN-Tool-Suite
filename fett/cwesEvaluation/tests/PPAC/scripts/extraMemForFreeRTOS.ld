/*
This file defines link.ld macros to increase the memory (stack + heap).
This is included when running PPAC on 64-bit FreeRTOS.
*/

_STACK_SIZE = 128K;
_HEAP_SIZE = 8M;
_DMEM_LENGTH = 0x04000000;
