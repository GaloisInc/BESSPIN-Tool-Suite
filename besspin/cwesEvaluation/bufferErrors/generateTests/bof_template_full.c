/*
 * Automatically generated buffer error
 *
 * Template Parameters used:
 * {tp}
 *
 * Instantiated Bugs Framework with:
 * {bf_bof}
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
// BUF_ACCESS = (PTR_ACCESS, ARRAY_ACCESS)
#define {buf_access}
// LOCATION = (STACK, HEAP)
#define {location}

// BUF2 = (BUF2_PRESENT, BUF2_ABSENT)
#define {buf2}

// ARG_TYPE = (FIXED_ARGS, VARIADIC_ARGS)
#define {arg_type}

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

{global_decls}

/*****************************
 * Functions
 * **************************/


/** DISABLED
#ifdef VAR_ARGS
{fun_ret_type} {fun_name} (int _n, ...)
#else //FIXED_ARGS
*/
//{fun_ret_type} {fun_name} ({fun_params_decl})
/** DISABLED
#endif//VAR_ARGS
*/
{{
/** DISABLED
#ifdef VAR_ARGS
  va_list argp;
  va_start(argp, _n);
  {arg_assignment_stmts}
  va_end(argp);
#endif //VAR_ARGS
*/
    /*
     * Declarations
     */
    {bof_fun_decls}

    //temp var
    {tmp_var_type} {tmp_var_name};

#ifdef STACK
    {buf_type} {buf_name}[{N}] = {{0}};
#else //HEAP
    {buf_type}* {buf_name} = malloc(sizeof({buf_type})*{N});
#endif//STACK


#ifdef STACK
#ifdef BUF2_PRESENT
    {buf_type2} {buf_name2}[{N2}] = {{0}};
#endif//BUF2_PRESENT
#endif//STACK

#ifdef LOOP
    /*
     * Buffer Access: Read/Write
     */
    for(int idx={idx0}; idx{relop}({idx0}+{access_len}); idx=idx+{incr})
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

#endif//LOOP


#ifdef JMP
    longjmp(env, 2);
#else// RETURN
    // TODO: Return what value?
    {bof_fun_return_stmt}
#endif//JMP
}}


/*
 * Main Function
 *
 */
int main()
{{

#ifdef JMP
    int jmp_return = setjmp(env);
    if (jmp_return != 0)
    exit(0);
#endif
    {main_fun_body}

#ifdef BARE_RISCV_SIM
    TEST_PASS
#endif
    return 0;

}}
