/* This is the CWE test template
- MAIN(_)DECLARATION will be substituted by the test's main function declaration
- TEST(_)NAME will be substituted by the test's main function name
*/

#include <stdio.h>

#ifdef testgenFPGA
    #include <FreeRTOS.h>
    #include <task.h>

    void vMain (void *pvParameters);
#endif

void main_fett (void);

extern MAIN_DECLARATION;

void main_fett (void)
{
    printf (">>>Beginning of Fett<<<\n");

    #ifdef testgenFPGA
        // Execute tests within a task to accommodate for security features that gets enabled with the scheduler
        BaseType_t funcReturn = xTaskCreate(vMain,
                                            "main:vMain",
                                            configMINIMAL_STACK_SIZE * 10,
                                            NULL,
                                            tskIDLE_PRIORITY + 1,
                                            NULL);

        if (funcReturn == pdPASS)
        {
            printf ("(INFO)~  main_fett: vMain task created.\n");
        } else {
            printf ("<INVALID>\n(ERROR)~ main_fett: Failed to create vMain task.\n");
        }
    #elif testgenQEMU
        main_TEST_NAME ();

        printf (">>>End of Fett<<<\n");
    #endif
    
    return;    
}

#ifdef testgenFPGA
    //This is the entry point task
    void vMain (void *pvParameters) {
        (void) pvParameters;

        printf ("(INFO)~ Beginning of Main Task.\n");

        main_TEST_NAME ();

        printf (">>>End of Fett<<<\n");

        vTaskDelete(NULL);
    }
#endif