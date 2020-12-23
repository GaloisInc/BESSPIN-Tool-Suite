/* This is the CWE test template
- MAIN(_)DECLARATION will be substituted by the test's main function declaration
- TEST(_)NAME will be substituted by the test's main function name
*/

#include <stdio.h>

void main_fett (void);

extern MAIN_DECLARATION;

void main_fett (void)
{
    printf (">>>Beginning of Fett<<<\n");

    main_TEST_NAME ();

    printf (">>>End of Fett<<<\n");
}
