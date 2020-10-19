/*
 * Automatically generated buffer error.
 *
 * params: {{ "template" : {tp}, "bof" : {bf_bof} }}
 *
*/

#ifndef NO_STDIO
#include <stdio.h>
#endif
#ifdef BARE_RISCV_SIM
#include "riscv_counters.h"
#endif

#if (defined(testgenOnFreeRTOS) && defined(testgenFPGA))
#include "FreeRTOS.h"
#endif

// READ_WRITE = (READ, WRITE)
#define {read_write}
// READ_AFTER_WRITE = (READ_AFTER_WRITE, NO_READ)
#define {read_after_write}
// BUF_ACCESS = (PTR_ACCESS, ARRAY_ACCESS)
#define {buf_access}
// LOCATION = (STACK, HEAP)
#define {location}
// EXCURSION = (CONTINUOUS, DISCRETE)
#define {excursion}
// COMPUTE_SIZE = (SIZE_OVERFLOW, NO_COMPUTE_SIZE)
#define {compute_size}

// BUF2 = (BUF2_PRESENT, BUF2_ABSENT)
#define {buf2}

#define {fun_bof_return}


// (MEMCPY, LOOP)
#define {buf_cpy}

// Required for malloc's definition
#ifdef HEAP
#include <stdlib.h>
#endif

// Required for memset's definition
#ifdef STACK
#include <string.h>
#endif


#ifdef VAR_ARGS
#include<stdarg.h>
#endif

#ifdef JMP
#include<setjmp.h>
#include<stdlib.h>
#endif


/*****************************
 * Globals
 * **************************/

#ifdef JMP
jmp_buf env;
#endif

#if defined(testgenOnFreeRTOS) && defined(testgenFPGA)
extern uintptr_t __bss_end;
#endif

/*****************************
 * Functions
 * **************************/
void test(void);

#define SIZE(_ty, N, _max) \
  (((N*sizeof(_ty)) > _max) ? (_max/sizeof(_ty)) : N)

void test(void)
{{
#ifdef SIZE_OVERFLOW
    // If the buffer were `max_index` long, there would be no overruns
    // (remember, Int_Overflow_To_Buffer_Overflow implies Boundary_Above).
    // This calculation uses `max_index` rather than adding 2 numbers together
    // that sum to `N` because it's more realistic to have a size calculation
    // that's partially correct, but later overflowed.
    size_t {max_index} = {idx0} + {access_len} + 1;
    // Arrive at N via overflow
    size_t {buf_size} = {max_index} + ((~((size_t) 0)) - {max_index} + {N}) + 1;
#else
    size_t {buf_size} = {N};
#endif

    //temp var
    {tmp_var_type} {tmp_var_name};

#ifdef STACK
    // Cleared via memset so that we can do error checking
    // without wiping OS structures (ie if we overflowed into bss)
    {buf_type} {buf_name}[SIZE({buf_type},{buf_size},{memmax})];

#if defined(testgenOnFreeRTOS) && defined(testgenFPGA)
    if (&{buf_name}[0] <= (uintptr_t)&__bss_end) {{
            printf("TEST INVALID. <buf1>\r\n");
            fflush(stdout);
            return;
    }}
#endif //FreeRTOS
    memset({buf_name}, 0, sizeof({buf_type})*SIZE({buf_type},{buf_size},{memmax}));

#else //HEAP
#ifdef testgenOnFreeRTOS
    {buf_type}* {buf_name} = pvPortMalloc(sizeof({buf_type})*SIZE({buf_type},{buf_size},{memmax}));
#else
    {buf_type}* {buf_name} = malloc(sizeof({buf_type})*SIZE({buf_type},{buf_size},{memmax}));
#endif
    if ({buf_name} == NULL) {{
            printf("TEST INVALID. <malloc>\r\n");
#ifdef testgenOnFreeRTOS
            printf("<xPortGetFreeHeapSize() = %x>\r\n", xPortGetFreeHeapSize());
#endif
            fflush(stdout);
            return;
    }} else {{
            printf("<valid malloc result>\r\n");
            fflush(stdout);
    }}
#endif

#ifdef STACK
#ifdef BUF2_PRESENT
    {buf_type2} {buf_name2}[SIZE({buf_type2},{N2},{memmax})];

#if defined(testgenOnFreeRTOS) && defined(testgenFPGA)
    if (&{buf_name2}[0] <= (uintptr_t)&__bss_end) {{
            printf("TEST INVALID. <buf2>\r\n");
            fflush(stdout);
            return;
    }}
    memset({buf_name}, 0, sizeof({buf_type})*SIZE({buf_type},{buf_size},{memmax}));
#endif//FREERTOS
#endif//BUF2_PRESENT
#endif//STACK

             printf("continous\r\n");
             fflush(stdout);
#ifdef CONTINUOUS
    printf("<begin continuous read/write>\r\n");
    fflush(stdout);
    for(int idx={c_idx0}; idx{relop}({c_idx0}+{c_access_len}); idx=idx+{c_incr})
    {{
#ifdef READ
#ifdef PTR_ACCESS
                {tmp_var_name} = *({buf_name} + idx);
#else //ARRAY_ACCESS
                {tmp_var_name} = {buf_name}[idx];
#endif
#else //WRITE
#ifdef PTR_ACCESS
                *({buf_name} + idx) = {tmp_var_name};
#else //ARRAY_ACCESS
                {buf_name}[idx] = {tmp_var_name};
#endif
#endif//READ
    }}
    printf("<end continuous read/write>\r\n");
    fflush(stdout);
#endif // CONTINUOUS

             printf("loop\r\n");
             fflush(stdout);
#ifdef LOOP
    printf("<begin overflow read/write loop>\r\n");
    fflush(stdout);
    /*
     * Buffer Access: Read/Write
     */
#define BOF_FOR_LOOP \
    for(int idx={idx0}; idx{relop}({idx0}+{access_len}); idx=idx+{incr})

    BOF_FOR_LOOP
    {{
            /* Attempt to catch the case where we overwrite idx, causing non-termination */
            if ((({incr} < 0) && (idx > {idx0})) ||
                (({incr} > 0) && (idx < {idx0})))
            {{
                /* If we are here, then somehow 'idx' is GREATER than its initial value
                   even though it is monotonically DECREASING (resp. LESS/INCREASING) */
                printf("<write to idx detected>\r\n");
                fflush(stdout);
                break;
            }}

#ifdef READ
    #ifdef PTR_ACCESS
         {tmp_var_name} = *({buf_name} + idx);
    #else //ARRAY_ACCESS
         {tmp_var_name} = {buf_name}[idx];
    #endif
#else //WRITE
    #ifdef PTR_ACCESS
         *({buf_name} + idx) = {tmp_var_name};
    #else //ARRAY_ACCESS
         {buf_name}[idx] = {tmp_var_name};
    #endif
#endif//READ
    }}
    printf("<end overflow read/write loop>\r\n");
    fflush(stdout);
#endif//LOOP

#ifdef READ_AFTER_WRITE
    printf("<begin overflow read-after-write loop>\r\n");
    fflush(stdout);
    BOF_FOR_LOOP
    {{
    #ifdef PTR_ACCESS
         {tmp_var_name} = *({buf_name} + idx);
    #else //ARRAY_ACCESS
         {tmp_var_name} = {buf_name}[idx];
    #endif
    }}
    printf("<end overflow read-after-write loop>\r\n");
#endif
             printf("done\r\n");
             fflush(stdout);

#ifdef JMP
    longjmp(env, 2);
#else// RETURN
    return;
#endif//JMP
}}


/*
 * Main Function
 *
 */
int main()
{{
    setbuf(stdout, NULL);
    printf("<BufferErrors Start>\r\n");
    fflush(stdout);

#ifdef JMP
    int jmp_return = setjmp(env);
    if (jmp_return != 0)
        goto COMPLETE;
#endif
    test();

    COMPLETE:
    printf("TEST COMPLETED\n");
#ifdef BARE_RISCV_SIM
    TEST_PASS
#endif
    return 0;

}}
