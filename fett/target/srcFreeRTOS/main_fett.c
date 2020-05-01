// This is the main function executed by fett -- It is just a wrapper

#include "fettFreeRTOS.h"

void main_fett (void);

TaskHandle_t xMainTask = NULL;
UBaseType_t xMainPriority = tskIDLE_PRIORITY+100; //100 is chosen arbitrarily.

//Define main apps + other tests
#if defined(FETT_HTTPS)
    extern void vHttps (void *pvParameters);
    #define vApp vHttps
#elif defined(FETT_OTA)
    extern void vOta (void *pvParameters);
    #define vApp vOta
#endif

void main_fett () {

    printf ("\n>>>Beginning of Fett<<<\n");

    BaseType_t funcReturn = xTaskCreate(vApp, "main:task", configMINIMAL_STACK_SIZE * STACKSIZEMUL, NULL, xMainPriority, NULL);
    prERROR_IF_NEQ(funcReturn, pdPASS, "main_fett: Creating vApp task.");

    vTaskStartScheduler(); //Hang the function
    return;
}
