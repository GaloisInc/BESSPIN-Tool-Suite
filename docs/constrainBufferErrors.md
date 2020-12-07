# Further Constraining Buffer Errors Tests #

This document details how to to constrain the buffer errors test suite
to generate tests that stress a more narrow class of errors than the default
test suite.

## Buffer Errors Clafer ##

The buffer errors clafer file
(`fett/cwesEvaluation/bufferErrors/buffErrors.cfr`) defines a set of program
constraints and specifies a mapping from CWEs to constraints.  You
may force the setting of certain constraints by listing them at the end of the
`BufferErrors_Test` section.  For example, if you'd like to only generate stack
tests, rather than a mix of stack and heap tests, you should add
`[Location_Stack]` to the end of the clafer file (indented by two spaces to
apply it to the `BufferErrors_Test` section).  You may add as many constraints
as you'd like, and the tool will take their conjunction.  You should not remove
any definitions from this file.

### Important Configuration Changes ###

If you modify the clafer file, you must also make the following changes to
the `bufferErrors` section of `config.ini`:

* Set `useCachedInstances` to `No` for the first run.  This will cause the tool
  to regenerate the set of instances that the clafer file defines.  Depending
  on how you've modified the file, this may take a while to run (up to half an
  hour or so).  After running to tool to completion, you may re-enable
  `useCachedInstances`.  You must disable `useCachedInstances` for the first
  run every time you modify the clafer file.
* Set `enforceQuotas` to `No`.  This option must be disabled any time you
  use a custom clafer file.

## Constraining Numeric Types ##

By default, the tool will generate tests that stress a variety of integer and
floating point tests.  You may restrict it to generate only integer or floating
point tests by modifying the `numericTypes` option in the `bufferErrors`
section of `config.ini`.

## Example ##

Say you would like to constrain the tool to only generate indexed array
buffer errors in the stack with a magnitude of close and only using integer
types.  Here are the steps you would take to accomplish this:

1. Make the following changes to the `bufferErrors` section of `config.ini`:
  * Set `useCachedInstances` to `No`
  * Set `enforceQuotas` to `No`
  * Set `numericTypes` to `[ints]`
2. Add the following lines to the bottom of
   `fett/cwesEvaluation/bufferErrors/buffErrors.cfr`:
```
  [BufferIndexScheme_IndexArray]
  [Location_Stack]
  [Magnitude_Close]
```
  The final file will look like:
```
// Model of BufferError vulnerabilities
// and concrete tests
abstract BufferErrors_Weakness
  xor Access
    Access_Read
    Access_Write

  xor Boundary
    Boundary_Below
    Boundary_Above

  xor Location
    Location_Stack
    Location_Heap
    
  xor Magnitude
    Magnitude_VeryClose
    Magnitude_Close
    Magnitude_Far

  xor DataSize
    DataSize_Little
    DataSize_Some
    DataSize_Huge

  xor Excursion
    Excursion_Continuous
    Excursion_Discrete

BufferErrors_Test : BufferErrors_Weakness ?

  Access_Read_After_Write ?
  [ !Access_Write => !Access_Read_After_Write ]

  xor SizeComputation
    SizeComputation_None
    SizeComputation_IntOverflowToBufferOverflow
    SizeComputation_IncorrectMallocCall
  [ Boundary_Below => SizeComputation_None ]
  [ Location_Stack => !SizeComputation_IncorrectMallocCall ]

  xor BufferIndexScheme
    BufferIndexScheme_PointerArithmetic
    BufferIndexScheme_IndexArray

  or CWE
    CWE_118
    CWE_119
    CWE_120
    CWE_121
    CWE_122
    CWE_123
    CWE_124
    CWE_125
    CWE_126
    CWE_127
    CWE_129
    CWE_130
    CWE_131
    CWE_680
    CWE_786
    CWE_787
    CWE_788
    CWE_823

    [ CWE_118 ]
    [ CWE_119 ]
    [ CWE_120 <=> ( Boundary_Above && Access_Write && Excursion_Continuous ) ]
    [ CWE_121 <=> ( Location_Stack && Access_Write ) ]
    [ CWE_122 <=> ( Location_Heap  && Access_Write ) ]
    [ CWE_123 <=> ( Access_Write ) ]
    [ CWE_124 <=> ( Boundary_Below && Access_Write ) ]
    [ CWE_125 <=> ( Access_Read ) ]
    [ CWE_126 <=> ( Boundary_Above && Access_Read ) ]
    [ CWE_127 <=> ( Boundary_Below && Access_Read ) ]
    [ CWE_129 <=> ( BufferIndexScheme_IndexArray ) ]
    [ CWE_130 <=> ( SizeComputation_IncorrectMallocCall ) ]
    [ CWE_131 <=> ( SizeComputation_IntOverflowToBufferOverflow ||
                    SizeComputation_IncorrectMallocCall ) ]
    [ CWE_680 <=> ( SizeComputation_IntOverflowToBufferOverflow ) ]
    [ CWE_786 <=> ( Boundary_Below ) ]
    [ CWE_787 <=> ( Access_Write) ]
    [ CWE_788 <=> ( Boundary_Above ) ]
    [ CWE_823 <=> ( BufferIndexScheme_PointerArithmetic ) ]

  [BufferIndexScheme_IndexArray]
  [Location_Stack]
  [Magnitude_Close]
// End of BufferErrors
```
3. Run Fett
4. Optionally disable `useCachedInstaces` in `config.ini` if you plan on
   re-running Fett with the same clafer file.
