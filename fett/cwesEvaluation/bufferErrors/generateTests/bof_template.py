import random
import string
import math

from fett.cwesEvaluation.bufferErrors.generateTests.bof_instance import *
from fett.base.utils.misc import *

class Dep:
    def __init__(self, x, makeGen):
        self.var = x
        self.makeGen = makeGen

    def getRand(self, rnd, env=None):
        if self.var in env:
            return self.makeGen(env[self.var]).getRand(rnd, env)
        else:
            return None

class Choice:
    def __init__(self, *vals):
        self.vals = vals

    def getRand(self, rnd, env=None):
        return rnd.choice(self.vals)

class Range:
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def getRand(self, rnd, env=None):
        return rnd.randint(self.lo, self.hi)

class Name:
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

def sizeof(typ):
    if typ == "float":
        return 4
    if typ == "double":
        return 8
    if typ[0] == 'u':
        # drop "uint" and "_t"
        bits = int(typ[4:-2])
    else:
        # drop "int" and "_t"
        bits = int(typ[3:-2])
    return bits // 8

C_MULTIBYTE_INTEGRAL_TYPES = [ 'int16_t', 'int32_t', 'int64_t' ]
C_FLOATING_TYPES = [ 'float', 'double' ]
C_MULTIBYTE_TYPES = [ f"{q}{t}" for q in ['', 'u'] for t in C_MULTIBYTE_INTEGRAL_TYPES] \
                   + C_FLOATING_TYPES
C_TYPES = C_MULTIBYTE_TYPES + ['int8_t', 'uint8_t']

## Derive C Template values from BOF attributes
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
    b = math.log(bound)/3.0
    return { 'DataSize_Little' : (1, math.ceil(math.exp(b))),
             'DataSize_Some'   : (1 + math.ceil(math.exp(b)), math.ceil(math.exp(2*b))),
             'DataSize_Huge'   : (1 + math.ceil(math.exp(2*b)), math.ceil(math.exp(3*b))) }

def pickDataRange(attr, bound):
    sz = DATASIZE(bound)[attr]
    if sz[1] > bound:
        return Range(sz[0], bound)
    return Range(sz[0], sz[1])

class BofTestGen:
    def __init__(self, bof_instance, heapSize, stackSize):
        self.bof_instance = bof_instance
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
        above = bof_instance.Boundary == 'Boundary_Above'
        incorrect_malloc = (bof_instance.SizeComputation ==
                            "SizeComputation_IncorrectMallocCall")
        mag   = MAGNITUDE[bof_instance.Magnitude]
        magRange = Range(mag[0], mag[1]) if above else Range(0-mag[1], 0-mag[0])
        memBound = heapSize if bof_instance.Location == 'HEAP' else stackSize
        dataRange = pickDataRange(bof_instance.DataSize, memBound)

        def chooseIdx0(N):
            r = mag
            if incorrect_malloc:
                # Choose an idx0 that would be in range if malloc was correct,
                # but is out of range with the incorrect malloc call
                def computeLowerBound(buf_type):
                    type_size = sizeof(buf_type)
                    min_index = (N + r[0]) // type_size
                    max_index = min(N-1, min_index + (r[1] // type_size))
                    return Range(min_index, max_index)
                return Dep("buf_type", computeLowerBound)
            else:
                if above:
                    r = (N + r[0], N + r[1])
                else:
                    r = (0 - r[1], 0 - r[0])
                return Range(r[0], r[1])

        def chooseCIdx0(N):
            if incorrect_malloc:
                def computeUpperBound(buf_type):
                    max_index = N // sizeof(buf_type)
                    return Range(0, max_index-1)
                return Dep('buf_type', computeUpperBound)
            return Range(0, N-1)

        def chooseIncr(x):
            if above:
                if x <= 1:
                    return Choice(1)
                return Range(1, x)
            else:
                if x >= -1:
                    return Choice(-1)
                return Range(x, -1)

        def chooseRange():
            if incorrect_malloc:
                def bindN(N):
                    def bindIdx(idx):
                        return Range(1, N-idx)
                    return Dep('idx0', bindIdx)
                return Dep('N', bindN)
            return magRange

        def chooseCRange(N):
            def go(idx):
                if incorrect_malloc:
                    def bindBufType(buf_type):
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
            test.
            """
            s = sizeof(buf_type)
            return max(s, math.ceil(mag[0] / (s - 1)) + 1)

        def chooseBufType():
            if incorrect_malloc:
                # Filter out types that won't produce legal N values
                legal_types = [x for x in C_MULTIBYTE_TYPES if
                               incorrectMallocMinN(x) <= dataRange.hi]
                return Choice(*legal_types)
            return Choice(*C_TYPES)

        def chooseN():
            if incorrect_malloc:
                def bindBufType(buf_type):
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

            'N'                : chooseN(),
            'N2'               : dataRange,

            # These should be set by 'magnitude'
            'idx0'             : Dep('N', chooseIdx0),
            'access_len'       : chooseRange(),
            'incr'             : Dep('access_len', chooseIncr),

            'memmax'           : Choice(memBound),

            'buf_name'         : Name("buf", 3, 15),
            'buf_name2'        : Name("buf2", 3, 15),
            'tmp_var_name'     : Name("tmp", 3, 15),

            'excursion'        : Choice(excursion),
            'c_idx0'           : Dep('N', chooseCIdx0),
            'c_access_len'     : Dep('N', chooseCRange),
            'c_incr'           : Dep('c_access_len', chooseIncr),

            'buf_type'         : chooseBufType(),
            'buf_type2'        : Choice(*C_TYPES),
            'tmp_var_type'     : Choice(*C_TYPES),

            'buf_access'       : Choice(SCHEME[bof_instance.BufferIndexScheme]),
            'buf_cpy'          : Choice('LOOP'),# 'MEMCPY'),
            'relop'            : Choice('<=') if above else Choice('>='),
            'location'         : Choice(LOCATION[bof_instance.Location]),
            'read_write'       : Choice(ACCESS[bof_instance.Access]),
            'buf2'             : Choice('BUF2_PRESENT', 'BUF2_ABSENT'),
            'fun_bof_return'   : Choice('JMP', 'RETURN'),
            'read_after_write' : read_after_write,

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

