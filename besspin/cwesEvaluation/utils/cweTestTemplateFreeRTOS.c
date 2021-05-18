/* This is the CWE test template
- MAIN(_)DECLARATION will be substituted by the test's main function declaration
- TEST(_)NAME will be substituted by the test's main function name
*/

#include <stdio.h>

#ifdef BESSPIN_FPGA
    #include <FreeRTOS.h>
    #include <task.h>

    void vMain (void *pvParameters);
#endif

void main_besspin (void);

extern MAIN_DECLARATION;

void main_besspin (void)
{
    printf (">>>Beginning of Besspin<<<\n");

    #ifdef BESSPIN_FPGA
        // Execute tests within a task to accommodate for security features that gets enabled with the scheduler
        BaseType_t funcReturn = xTaskCreate(vMain,
                                            "main:vMain",
                                            configMINIMAL_STACK_SIZE * 10,
                                            NULL,
                                            tskIDLE_PRIORITY + 1,
                                            NULL);

        if (funcReturn == pdPASS)
        {
            printf ("(INFO)~  main_besspin: vMain task created.\n");
        } else {
            printf ("<INVALID>\n(ERROR)~ main_besspin: Failed to create vMain task.\n");
        }
    #elif BESSPIN_QEMU
        main_TEST_NAME ();

        printf (">>>End of Besspin<<<\n");
    #endif
    
    return;    
}

#ifdef BESSPIN_FPGA
    //This is the entry point task
    void vMain (void *pvParameters) {
        (void) pvParameters;

        printf ("(INFO)~ Beginning of Main Task.\n");

        main_TEST_NAME ();

        printf (">>>End of Besspin<<<\n");

        vTaskDelete(NULL);
    }
#endif