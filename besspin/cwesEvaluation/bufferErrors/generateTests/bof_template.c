/*
 * Automatically generated buffer error.
 *
 * params: {{ "template" : {tp}, "bof" : {bf_bof} }}
 *
*/

// For fixed width integers
#include <stdint.h>

#ifndef NO_STDIO
#include <stdio.h>
#endif
#ifdef BARE_RISCV_SIM
#include "riscv_counters.h"
#endif

#if (defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA))
#include "FreeRTOS.h"
#endif

// READ_WRITE = (READ, WRITE)
#define {read_write}
// READ_AFTER_WRITE = (READ_AFTER_WRITE, NO_READ)
#define {read_after_write}
// BUF_ACCESS = (PTR_ACCESS, ARRAY_ACCESS, PATH_MANIPULATION_ACCESS)
#define {buf_access}
// LOCATION = (STACK, HEAP, GLOBAL)
#define {location}
// EXCURSION = (CONTINUOUS, DISCRETE)
#define {excursion}
// COMPUTE_SIZE = (SIZE_OVERFLOW, INCORRECT_MALLOC_CALL, NO_COMPUTE_SIZE)
#define {compute_size}

// BUF2 = (BUF2_PRESENT, BUF2_ABSENT)
#define {buf2}

#define {fun_bof_return}

// ALLOC_TYPE = (STATIC_ALLOC, DYNAMIC_ALLOC)
#define {alloc_type}

// (MEMCPY, LOOP)
#define {buf_cpy}

// Required for malloc's definition
#ifdef HEAP
#include <stdlib.h>
#endif

// Required for memset's definition
#if (defined(STACK) || defined(GLOBAL))
#include <string.h>
#endif

#ifdef VAR_ARGS
#include<stdarg.h>
#endif

#ifdef JMP
#include<setjmp.h>
#include<stdlib.h>
#endif

#if defined(PATH_MANIPULATION_ACCESS) && !defined(BESSPIN_FREERTOS) && !defined(BESSPIN_BARE_METAL)
// Required for realpath
#include <limits.h>
#include <stdlib.h>
// Required for strnlen
#include <string.h>
#define MIN(a,b) (((a)<(b))?(a):(b))
#endif


/*****************************
 * Globals
 * **************************/

#ifdef JMP
jmp_buf env;
#endif

#ifdef GLOBAL
    {buf_type} {buf_name}[{N}];

    #ifdef BUF2_PRESENT
        {buf_type2} {buf_name2}[{N2}];
    #endif
#endif

/*****************************
 * Functions
 * **************************/
void test_buffer_overflow(void);

#define SIZE(_ty, N, _max) \
  (((N*sizeof(_ty)) > _max) ? (_max/sizeof(_ty)) : N)

#ifdef INCORRECT_MALLOC_CALL
/*
 * These functions exist to test CWE-130 (Improper Handling of Length Parameter
 * Inconsistency).  They simulate the API a programmer may use to allocate
 * space for a message recieved over the network.  `mock_get_message_size`
 * simulates a function that returns the size of the message in units of
 * `buf_type`.  `allocate_message_buf` allocates a buffer to hold the message,
 * but incorrectly treats the result of `mock_get_message_size` as the number
 * of bytes to allocate, rather than the number of elements.  As such, it
 * returns a buffer that is much too small.  The python test generator chooses
 * values for the various parameters in this test that would be in bounds if
 * `allocate_message_buf` were implemented correctly and allocated a buffer of
 * size `mock_get_message_size() * sizeof(buf_type)`.
 */
size_t mock_get_message_size(void);
{buf_type}* allocate_message_buf(void);

size_t mock_get_message_size(void) {{
  return {N};
}}

{buf_type}* allocate_message_buf(void) {{
  // Misinterpret the result of `mock_get_message_size` as a size in bytes,
  // rather than the number of elements of type `buf_type` the message has.
  size_t {alloc_bytes} = SIZE(char, mock_get_message_size(), {memmax});
#if defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA)
  return pvPortMalloc({alloc_bytes});
#else
  return malloc({alloc_bytes});
#endif
}}
#endif  // INCORRECT_MALLOC_CALL

#ifdef SIZE_OVERFLOW
    // This is a simple manoeuver to avoid the compiler optimizing out the integer overflow. 
    // See #1130 for more details.
    static __attribute__((noinline)) size_t {sub_func} (size_t {sub_func_arg1}, size_t {sub_func_arg2}) {{
        size_t {sub_func_ret} = 0;
        {sub_func_ret} += {sub_func_arg1};
        {sub_func_ret} -= {sub_func_arg2};
        return {sub_func_ret};
    }}
#endif


void test_buffer_overflow(void)
{{
#ifdef SIZE_OVERFLOW
    // If the buffer were `min_size` long, there would be no overruns
    // (remember, SIZE_OVERFLOW implies Boundary_Above).
    // This calculation uses `min_size` rather than adding 2 numbers together
    // that sum to `N` because it's more realistic to have a size calculation
    // that's partially correct, but later overflowed.
    size_t {min_size} = {idx0} + {access_len} + 1;
    // Arrive at N via overflow
    size_t {buf_size} = {min_size} + ({sub_func}((~((size_t) 0)), {min_size}) + {N}) + 1;
    if ({buf_size} < {min_size}) {{
        // `buf_size` is too small, either because the overflow was undetected,
        // or because the value was replaced with one that is still too small.
        printf("BUFFER SIZE INSUFFICIENT\r\n");
        fflush(stdout);
    }} else {{
        // `buf_size` was altered by the processor to be sufficiently large.
        printf("BUFFER SIZE CORRECTED\r\n");
        fflush(stdout);
    }}
#else  // !SIZE_OVERFLOW
    size_t {buf_size} = {N};
#endif  // SIZE_OVERFLOW

    //temp var
    {tmp_var_type} {tmp_var_name};

#ifdef GLOBAL
    memset({buf_name}, 0, sizeof({buf_type})*{N});
#elif defined(STACK)
    // Cleared via memset so that we can do error checking
    // without wiping OS structures (ie if we overflowed into bss)
#ifdef STATIC_ALLOC
    if ({N} > SIZE({buf_type}, {N}, {memmax})) {{
        // Template generator should ensure this never happens, but double check
        // to be safe.
        printf("TEST INVALID. <N too large for static allocation>\r\n");
        return;
    }}
    {buf_type} {buf_name}[{N}];
    memset({buf_name}, 0, sizeof({buf_type})*{N});
#else  // DYNAMIC_ALLOC
    {buf_type} {buf_name}[SIZE({buf_type},{buf_size},{memmax})];
    memset({buf_name}, 0, sizeof({buf_type})*SIZE({buf_type},{buf_size},{memmax}));
#endif  // STATIC_ALLOC

#else //HEAP
#ifdef INCORRECT_MALLOC_CALL
    {buf_type}* {buf_name} = allocate_message_buf();
#else  // !INCORRECT_MALLOC_CALL
    size_t {alloc_bytes} = sizeof({buf_type})*SIZE({buf_type},{buf_size},{memmax});
#if defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA)
    {buf_type}* {buf_name} = pvPortMalloc({alloc_bytes});
#else
    {buf_type}* {buf_name} = malloc({alloc_bytes});
#endif  // defined(BESSPIN_FREERTOS) && defined(BESSPIN_FPGA)
#endif  // INCORRECT_MALLOC_CALL
    if ({buf_name} == NULL) {{
            printf("TEST INVALID. <malloc>\r\n");
#ifdef BESSPIN_FREERTOS
            printf("<xPortGetFreeHeapSize() = %x>\r\n", xPortGetFreeHeapSize());
#endif
            fflush(stdout);
            return;
    }} else {{
            printf("<valid malloc result>\r\n");
            fflush(stdout);
    }}
#endif // STACK/GLOBAL/HEAP

#ifdef BUF2_PRESENT

#ifdef GLOBAL
    memset({buf_name2}, 0, sizeof({buf_type2})*{N2});
#endif//GLOBAL

#ifdef STACK
#ifdef STATIC_ALLOC
    if ({N2} > SIZE({buf_type2}, {N2}, {memmax})) {{
        // Template generator should ensure this never happens, but double check
        // to be safe.
        printf("TEST INVALID. <N2 too large for static allocation>\r\n");
        return;
    }}
    {buf_type2} {buf_name2}[{N2}];
    memset({buf_name2}, 0, sizeof({buf_type2})*{N2});
#else  // DYNAMIC_ALLOC
    {buf_type2} {buf_name2}[SIZE({buf_type2},{N2},{memmax})];
    memset({buf_name2}, 0, sizeof({buf_type2})*SIZE({buf_type2},{N2},{memmax}));
#endif  //STATIC_ALLOC
#endif//STACK

#endif//BUF2_PRESENT

             printf("continous\r\n");
             fflush(stdout);
#ifdef CONTINUOUS
    printf("<begin continuous read/write>\r\n");
    fflush(stdout);
    for(int idx={c_idx0}; idx{relop}({c_idx0}+{c_access_len}); idx=idx+{c_incr})
    {{
#ifdef SIZE_OVERFLOW
            /* Attempt to catch the case where we overwrite idx, causing
             * non-termination.  Under most circumstances this loop is all in
             * bounds, but out of bounds writes are possible if SIZE_OVERFLOW
             * is defined and the processor sets `buf_size` to be less than `N`
             */
            if ((({c_incr} < 0) && (idx > {c_idx0})) ||
                (({c_incr} > 0) && (idx < {c_idx0})))
            {{
                /* If we are here, then somehow 'idx' is GREATER than its initial value
                   even though it is monotonically DECREASING (resp. LESS/INCREASING) */
                printf("<write to c_idx detected>\r\n");
                fflush(stdout);
                break;
            }}
#endif  // SIZE_OVERFLOW
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

#if defined(PATH_MANIPULATION_ACCESS) && !defined(BESSPIN_BARE_METAL)
void test_path_manipulation(void) {{
#ifdef BESSPIN_FREERTOS
    printf("TEST INVALID.  <not on FreeRTOS>\r\n");
    fflush(stdout);
#else
    if ({memmax} <= (PATH_MAX * sizeof(char))) {{
        // Not enough memory to perform both a proper and an improper realpath
        printf("TEST INVALID. <insufficient memory>\r\n");
        fflush(stdout);
        return;
    }}

    // Allocate {buf_name2} to hold the result of a proper realpath call
#ifdef STACK
    char {buf_name2}[PATH_MAX];
#else //HEAP (GLOBAL && PATH_MANIPULATION_ACCESS not allowed)
    char* {buf_name2} = malloc(sizeof(char) * PATH_MAX);
    if ({buf_name2} == NULL) {{
        printf("TEST INVALID. <malloc {buf_name2}>\r\n");
        fflush(stdout);
        return;
    }};
#endif

    // Expand "." into a properly sized buffer
    if (!realpath(".", {buf_name2})) {{
        printf("TEST INVALID. <realpath buf2>\r\n");
        fflush(stdout);
        return;
    }};

    // {tmp_var_name} represents the maximum size for {buf_name}.  {buf_name}
    // must be at most 1 byte smaller than what is required to store the path
    // expansion (including null terminator), so {tmp_var_name} is equal to the
    // strlen of {buf_name2}.
    size_t {tmp_var_name} = strnlen({buf_name2}, PATH_MAX);

    // Allocate {buf_name}
    size_t {buf_size} = SIZE(char,
                             ({N} % {tmp_var_name}) + 1,
                             {memmax} - (PATH_MAX * sizeof(char)));
#ifdef STACK
    char {buf_name}[{buf_size}];
#else //HEAP (GLOBAL && PATH_MANIPULATION_ACCESS not allowed)
    char* {buf_name} = malloc(sizeof(char) * {buf_size});
    if ({buf_name} == NULL) {{
        printf("TEST INVALID. <malloc>\r\n");
        fflush(stdout);
        return;
    }};
#endif

    // Call realpath with {buf_name}, which will overflow the buffer
    if (!realpath(".", {buf_name})) {{
        printf("TEST INVALID. <realpath buf>\r\n");
        fflush(stdout);
        return;
    }}

#ifdef JMP
    longjmp(env, 2);
#endif
#endif // !BESSPIN_FREERTOS
}};
#endif  // PATH_MANIPULATION_ACCESS && !BESSPIN_BARE_METAL

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

#ifdef PATH_MANIPULATION_ACCESS
#ifdef BESSPIN_BARE_METAL
    printf("TEST INVALID. <No realpath on bare metal>\r\n");
    fflush(stdout);
#else
    test_path_manipulation();
#endif
#else
    test_buffer_overflow();
#endif

    COMPLETE:
    printf("TEST COMPLETED\n");
#ifdef BARE_RISCV_SIM
    TEST_PASS
#endif
    return 0;

}}
