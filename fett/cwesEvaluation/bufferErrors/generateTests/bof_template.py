import random
import re
import string
import math

from fett.cwesEvaluation.bufferErrors.generateTests.bof_instance import *
from fett.base.utils.misc import *

###############################################################################
#### Parameter Assignment Classes
###############################################################################

'''
These classes are used to assign values to the various parameters that this
tool randomizes.  Each class has a function `getRand` that must return either a
random value, or `None`.  If the class returns `None`, then the class depends
on another parameter that is not yet assigned and the tool should call `getRand`
again later.  `getRand` takes as input a random object `rnd` and an optional
environment `env`, which is a dictionary mapping parameters to their values.
'''

class Dep:
    """
    This class represents a dependency.  Its constructor takes two parameters:
    x       : The parameter that this parameter depends on
    makeGen : A function that takes `x` as input and returns another parameter
              assignment class.

    `getRand` returns `makeGen(x).getRand(rnd, env)` if `x` is bound in `env`,
    otherwise it returns None.
    """
    def __init__(self, x, makeGen):
        self.var = x
        self.makeGen = makeGen

    def getRand(self, rnd, env=None):
        if self.var in env:
            return self.makeGen(env[self.var]).getRand(rnd, env)
        else:
            return None

class Choice:
    """
    `Choice` represents a random choice between multiple values.  Its
    constructor takes an arbitrary number of arguments, and a call to
    `getRand` returns a random element from the constructors arguments.
    """
    def __init__(self, *vals):
        self.vals = vals

    def getRand(self, rnd, env=None):
        return rnd.choice(self.vals)

class Range:
    """
    `Range` represents a random choice from a range.  Its constructor takes two
    parameters:
    lo : The low end of the range (inclusive)
    hi : The high end of the range (inclusive)

    `getRand` returns a random integer from `lo` through `hi` inclusive.
    """
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def getRand(self, rnd, env=None):
        return rnd.randint(self.lo, self.hi)

class Name:
    """
    `Name` represents a variable name in the generated C program.  Its
    constructor takes three parameters:
    prefix : The string prefix for the variable's name
    lo     : The minimum number of random characters to append to `prefix`
    hi     : The maximum number of random characters to append to `prefix`

    `getRand` returns a random variable name starting with `prefix` and ending
    in some number (between `lo` and `hi`) of random letters from the alphabet.
    `getRand` guarantees that it generates a unique name.  That is, even if
    there are two `Name` classes with the same `prefix`, `getRand` is
    guaranteed to produce different random strings for both.
    """
    seen = set([])
    alphabet = string.ascii_letters

    def __init__(self, prefix, lo, hi):
        self.prefix = prefix
        self.lo = lo
        self.hi = hi

    def getRand(self, rnd, env=None):
        while True:
            n = rnd.randint(self.lo, self.hi)
            suffix = "".join(rnd.choices(Name.alphabet, k=n))
            name = self.prefix + "_" + suffix
            if suffix not in Name.seen:
                Name.seen.add(name)
                return name

###############################################################################
#### Helper functions and constants
###############################################################################

def sizeof(typ):
    """ Given a C type name, returns the width of that type in bytes """
    if typ == "float":
        return 4
    if typ == "double":
        return 8
    int_match = re.fullmatch(r"u?int([0-9]{1,2})_t", typ)
    if int_match:
        try:
            # Extract width of the integer in bits from the type name and
            # divide by 8 to convert to bytes
            return int(int_match.group(1)) // 8
        except IndexError as exc:
            logAndExit("<sizeof> <int_match> has no group <1>",
                       exitCode=EXIT.Dev_Bug,
                       exc=exc)
        except ValueError as exc:
            logAndExit(f"<sizeof> Cannot interpret <{int_match.group(1)}> as "
                       "an int",
                       exitCode=EXIT.Dev_Bug,
                       exc=exc)
    logAndExit(f"<sizeof> Unknown type <{typ}>", exitCode=EXIT.Dev_Bug)

# The set of supported C integer types that are wider than 1 byte
C_MULTIBYTE_INTEGRAL_TYPES = [ 'int16_t', 'int32_t', 'int64_t' ]
# The set of supported C floating point types
C_FLOATING_TYPES = [ 'float', 'double' ]

## Derive C Template values from BOF attributes defined in Clafer file
MAGNITUDE    = { 'Magnitude_VeryClose' : (0, 10),
                 'Magnitude_Close'     : (10, 100),
                 'Magnitude_Far'       : (100, 1000) }
SCHEME       = { 'BufferIndexScheme_IndexArray' : 'ARRAY_ACCESS',
                 'BufferIndexScheme_PointerArithmetic' : 'PTR_ACCESS' }
ACCESS       = { 'Access_Read' : 'READ', 'Access_Write' : 'WRITE' }
LOCATION     = { 'Location_Stack' : 'STACK', 'Location_Heap' : 'HEAP' }
COMPUTE_SIZE = { 'SizeComputation_None' : 'NO_COMPUTE_SIZE',
                 'SizeComputation_IntOverflowToBufferOverflow' :
                     'SIZE_OVERFLOW',
                 'SizeComputation_IncorrectMallocCall' :
                     'INCORRECT_MALLOC_CALL' }

def DATASIZE(bound):
    """
    Define possible C buffer sizes based on `stackSize` and `heapSize`
    parameters from FETT config.
    """
    b = math.log(bound)/3.0
    return { 'DataSize_Little' : (1, math.ceil(math.exp(b))),
             'DataSize_Some'   : (1 + math.ceil(math.exp(b)), math.ceil(math.exp(2*b))),
             'DataSize_Huge'   : (1 + math.ceil(math.exp(2*b)), math.ceil(math.exp(3*b))) }

def pickDataRange(attr, bound):
    """
    Given a DataSize value from the clafer model `attr` and a memory bound from
    the FETT config `bound`, return a range of possible buffer sizes that
    satisfies both constraints.
    """
    sz = DATASIZE(bound)[attr]
    if sz[1] > bound:
        return Range(sz[0], bound)
    return Range(sz[0], sz[1])

###############################################################################
####  Test Generation
###############################################################################

class BofTestGen:
    """
    This class takes an instance from the BufferErrors clafer model, as well as
    the `heapSize` and `stackSize` constraints from the FETT config file and
    produces a C program that satisfies all of these constraints.  The program
    proceeds in 5 steps:

    1. Allocate a buffer `buf`
    2. If BUF2_PRESENT is #defined, allocate a second buffer `buf2`
    3. If CONTINUOUS is #defined, loop over `buf` performing in-bounds reads or
       writes
    4. Loop out of bounds over `buf` performing out-of-bounds reads or writes
    5. If READ_AFTER_WRITE is set, then repeat step 4 performing reads instead
       of writes.

    These 5 steps are referenced by number throughout the documentation of this
    class.

    The various parameters are described in the documentation for the
    self.PARAMS dictionary.
    """
    def __init__(self, bof_instance, heapSize, stackSize):
        self.bof_instance = bof_instance
        # The template file is essentially a long python f-string. This class
        # will fill in the values of this f-string using self.PARAMS
        templateFile = ftOpenFile(os.path.join(getSetting("repoDir"),
                                               "fett",
                                               "cwesEvaluation",
                                               "bufferErrors",
                                               "generateTests",
                                               "bof_template.c"),
                                  "r")
        self.template = templateFile.read()
        templateFile.close()

        # TODO: Configure these based on the input bof_instance
        # TODO: Add a 'machine' parameter to control size of memory

        # `above` is True if errors should occur after the end of the buffer,
        # and False if errors should occur before the beginning of the buffer.
        above = bof_instance.Boundary == 'Boundary_Above'

        # `incorrect_malloc` is True if the C test should misinterpret the size
        # parameter `N` as in bytes, rather than as elements of the buffer.
        incorrect_malloc = (bof_instance.SizeComputation ==
                            "SizeComputation_IncorrectMallocCall")
        # How far from the buffer the error should occur
        mag   = MAGNITUDE[bof_instance.Magnitude]
        # `magRange` is `mag` as a Range object
        magRange = Range(mag[0], mag[1]) if above else Range(0-mag[1], 0-mag[0])
        # Size of portion of memory under test
        memBound = heapSize if bof_instance.Location == 'HEAP' else stackSize
        # Range object representing the intersection between `magRange` and
        # memBound`
        dataRange = pickDataRange(bof_instance.DataSize, memBound)

        # The set of supported C types that are wider than 1 byte
        c_multibyte_types = []
        # The set of supported C types including those that are 1 byte wide
        c_types = []
        # Fill c_multibyte_types and c_types based on which types are enabled
        # in config.ini
        numeric_types = getSettingDict("bufferErrors", "numericTypes")
        if not numeric_types:
            logAndExit("<numericTypes> configuration option may not be empty",
                       exitCode=EXIT.Configuration)
        if "ints" in numeric_types:
            c_multibyte_types += [ f"{q}{t}" for q in ['', 'u'] for t in C_MULTIBYTE_INTEGRAL_TYPES]
            c_types += c_multibyte_types + ['int8_t', 'uint8_t']
        if "floats" in numeric_types:
            c_multibyte_types += C_FLOATING_TYPES
            c_types += C_FLOATING_TYPES

        def chooseIdx0(N):
            '''
            Choose the value of `idx0`.  `idx0` is the starting index for the
            out-of-bounds loop (step 4).  This choice depends on the value of
            `N`.  If `incorrect_malloc` is set, then it also depends on
            `buf_type`.
            '''
            r = mag
            if incorrect_malloc:
                # Choose an idx0 that would be in range if malloc was correct,
                # but is out of range with the incorrect malloc call
                def computeLowerBound(buf_type):
                    type_size = sizeof(buf_type)
                    # `min_index` is the smallest value that is out of bounds
                    # for `buf`
                    min_index = (N + r[0]) // type_size
                    # `max_index` is the largest value that would have been in
                    # bounds for `buf` if the malloc call was done correctly
                    max_index = min(N-1, min_index + (r[1] // type_size))
                    return Range(min_index, max_index)
                return Dep("buf_type", computeLowerBound)
            else:
                # Choose an idx0 that satisfies the `Magnitude` clafer
                # constraint.
                if above:
                    r = (N + r[0], N + r[1])
                else:
                    r = (0 - r[1], 0 - r[0])
                return Range(r[0], r[1])

        def chooseCIdx0(N):
            '''
            Choose the value of `c_idx0`.  `c_idx0` is the starting index for
            the in-bounds loop (step 3).  It depends on `N`.  If
            `incorrect_malloc` is defined, then `c_idx0` also depends on
            `buf_type`.
            '''
            if incorrect_malloc:
                # Choose a `cidx0` from 0 to `N // sizeof(buf_type)` to ensure
                # `cidx0` is in bounds
                def computeUpperBound(buf_type):
                    max_index = N // sizeof(buf_type)
                    return Range(0, max_index-1)
                return Dep('buf_type', computeUpperBound)
            # Choose a `cidx0` from 0 to `N-1`
            return Range(0, N-1)

        def chooseIncr(x):
            '''
            Choose the value of `incr`.  `incr` is the stride of the
            out-of-bounds loop (step 4).  It takes a parameter `x` representing
            the upper or lower bound of possible `incr` values.
            '''
            if above:
                if x <= 1:
                    return Choice(1)
                return Range(1, x)
            else:
                if x >= -1:
                    return Choice(-1)
                return Range(x, -1)

        def chooseRange():
            '''
            Choose the value of `access_len`.  `access_len` is the furthest
            distance from `idx0` that the out-of-bounds loop should access
            (step 4).  If `incorrect_malloc` is set, this choice depends on
            `N` and `idx`.
            '''
            if incorrect_malloc:
                # Choose a value that ensures the entire out-of-bounds loop
                # would have been in bounds if the malloc were correct
                def bindN(N):
                    def bindIdx(idx):
                        return Range(1, N-idx)
                    return Dep('idx0', bindIdx)
                return Dep('N', bindN)
            # Choose a value that satisfies the `Magnitude` constraint from the
            # model instance.
            return magRange

        def chooseCRange(N):
            '''
            Choose the value of `c_access_len`.  `c_access_len` is the furthest
            distance from `c_idx_0` that the in-bounds loop should access
            (step 3).  Depends on `N` and `idx`.  If `incorrect_malloc` is set,
            this function also depends on `buf_type`.
            '''
            def go(idx):
                if incorrect_malloc:
                    def bindBufType(buf_type):
                        # Divide `N` by the size of `buf_type` to ensure
                        # this loop remains in bounds
                        max_index = N // sizeof(buf_type)
                        return Range(1, max_index-idx)
                    return Dep('buf_type', bindBufType)
                if above:
                    return Range(1, N-idx)
                else:
                    return Range(-1*idx, 0)
            return Dep('c_idx0', go)

        def incorrectMallocMinN(buf_type):
            """
            Returns the minimum value (inclusive) of N in an incorrect malloc
            test that is both large enough to hold a single element of
            `buf_type`, and small enough to satisfy the `Magnitude` constraint
            from the clafer model instance.
            """
            s = sizeof(buf_type)
            return max(s, math.ceil(mag[0] / (s - 1)) + 1)

        def chooseBufType():
            """
            Chooses the value of `buf_type`.
            """
            if incorrect_malloc:
                # Filter out types that won't produce legal N values
                legal_types = [x for x in c_multibyte_types if
                               incorrectMallocMinN(x) <= dataRange.hi]
                return Choice(*legal_types)
            # Choose from all supported C types
            return Choice(*c_types)

        def chooseN():
            """
            Chooses the value of `N`.  `N` is the size of buffer.  If
            `incorrect_malloc` is set, then this depends on `buf_type` and `N`
            is in bytes.  Otherwise, `N` is in elements of `buf_type`.
            """
            if incorrect_malloc:
                def bindBufType(buf_type):
                    # Choose an `N` that is large enough to hold at least one
                    # `buf_type` element, but small enough to satisfy the data
                    # range.
                    minN = incorrectMallocMinN(buf_type)
                    return Range(max(minN, dataRange.lo), dataRange.hi)
                return Dep('buf_type', bindBufType)
            return dataRange

        # Excursion_Continuous => CONTINUOUS
        excursion = bof_instance.Excursion.split("_")[1].upper()

        read_after_write = Choice("READ_AFTER_WRITE" if
                                  bof_instance.Access_Read_After_Write else
                                  "NO_WRITE")

        self.PARAMS = {
            # Size of the buffer.  In bytes if `incorrect_malloc` is set,
            # otherwise in elements of `buf_type`.
            'N'                : chooseN(),
            # Size of `buf2` in number of elements.
            'N2'               : dataRange,

            # Starting index of out-of-bounds loop (step 4)
            'idx0'             : Dep('N', chooseIdx0),
            # The furthest distance from `idx0` the out-of-bounds loop should
            # access (step 4).
            'access_len'       : chooseRange(),
            # The stride of the out of bounds loop (step 4).
            'incr'             : Dep('access_len', chooseIncr),

            # Size of heap or stack memory available
            'memmax'           : Choice(memBound),

            # Name of buffer to overrun
            'buf_name'         : Name("buf", 3, 15),
            # Name of second buffer
            'buf_name2'        : Name("buf2", 3, 15),
            # Name of temporary var
            'tmp_var_name'     : Name("tmp", 3, 15),

            # CONTINUOUS to enable in-bounds loop (step 3).  DISCRETE to
            # disable in-bounds loop.
            'excursion'        : Choice(excursion),
            # Starting index of in-bounds loop (step 3).
            'c_idx0'           : Dep('N', chooseCIdx0),
            # Furthest distance from `c_idx0` the in-bounds loop should access
            # (step 3)
            'c_access_len'     : Dep('N', chooseCRange),
            # Stride of in bounds loop (step 3)
            'c_incr'           : Dep('c_access_len', chooseIncr),

            # Type of data `buf` stores
            'buf_type'         : chooseBufType(),
            # Type of data `buf2` stores
            'buf_type2'        : Choice(*c_types),
            # Type of the temporary variable
            'tmp_var_type'     : Choice(*c_types),

            # Whether to access the buffer via array indexing or pointer
            # arithmetic
            'buf_access'       : Choice(SCHEME[bof_instance.BufferIndexScheme]),
            # Whether to loop or use memcpy (memcpy not supported)
            'buf_cpy'          : Choice('LOOP'),# 'MEMCPY'),
            # Which relational operator to use in the loops
            'relop'            : Choice('<=') if above else Choice('>='),
            # Whether to place the buffers on the stack or heap
            'location'         : Choice(LOCATION[bof_instance.Location]),
            # Whether access should be reads or writes
            'read_write'       : Choice(ACCESS[bof_instance.Access]),
            # Whether `buf2` should exist
            'buf2'             : Choice('BUF2_PRESENT', 'BUF2_ABSENT'),
            # Whether the test function should jump or return
            'fun_bof_return'   : Choice('JMP', 'RETURN'),
            # Whether to perform out-of-bounds reads (step 5) after
            # out-of-bounds writes (step 4)
            'read_after_write' : read_after_write,

            # How to derive the size of the buffer.  Options:
            #  SIZE_OVERFLOW         : Via integer overflow
            #  INCORRECT_MALLOC_CALL : Via misinterpretation of the size
            #                          parameter `N`
            #  NO_COMPUTE_SIZE       : Using hard coded `N` value
            'compute_size'     : Choice(COMPUTE_SIZE[bof_instance.SizeComputation]),
            # Variable holding smallest buffer size that will cover all reads
            # and writes.  Only used if SIZE_OVERFLOW is defined.
            'min_size'        : Name("min_size", 3, 15),
            # Variable holding the size of `buf`
            'buf_size'        : Name("buf_size", 3, 15),
            # Variable holding the number of bytes to allocate in heap tests
            'alloc_bytes'     : Name("alloc_bytes", 3, 15)
        }

    def genInstance(self, rnd, drop=False):
        ## This is a little complicated, but since the number of params is low
        ## we can be less than smart about it.

        ## What we need to do is iteratively pick values for each param. Some
        ## params may have dependencies (i.e. idx0 depends on N), so we'll
        ## un-cleverly try to do our best by looping through the params until
        ## we're all done. That way I don't need to remember how to do a topological sort :)
        i = {}
        queue = list(self.PARAMS.keys())
        lastlen = 0
        while len(queue) > 0:
            k     = queue[0]
            queue = queue[1:]
            v     = self.PARAMS[k].getRand(rnd, env=i)
            if v is not None:
                i[k] = v
            else:
                queue.append(k)
        i['tp']     = json.dumps(i)
        i['bf_bof'] = json.dumps(vars(self.bof_instance))

        if not drop:
            return self.template.format(**i)

