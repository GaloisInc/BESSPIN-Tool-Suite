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

C_INTEGRAL_TYPES = [ 'char', 'short', 'int', 'long' ]
C_FLOATING_TYPES = [ 'float', 'double' ]
C_TYPES          = [ f"{q} {t}" for q in ['signed', 'unsigned'] for t in C_INTEGRAL_TYPES] \
                   + C_FLOATING_TYPES

## Derive C Template values from BOF attributes
MAGNITUDE = { 'Magnitude_VeryClose' : (0, 10),
              'Magnitude_Close'     : (10, 100),
              'Magnitude_Far'       : (100, 1000) }
SCHEME    = { 'BufferIndexScheme_IndexArray' : 'ARRAY_ACCESS',
              'BufferIndexScheme_PointerArithmetic' : 'PTR_ACCESS' }
ACCESS    = { 'Access_Read' : 'READ', 'Access_Write' : 'WRITE' }
LOCATION  = { 'Location_Stack' : 'STACK', 'Location_Heap' : 'HEAP' }

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
        mag   = MAGNITUDE[bof_instance.Magnitude]
        magRange = Range(mag[0], mag[1]) if above else Range(0-mag[1], 0-mag[0])

        def chooseIdx0(N):
            r = mag
            if above:
                r = (N + r[0], N + r[1])
            else:
                r = (0 - r[1], 0 - r[0])
            return Range(r[0], r[1])

        def chooseCIdx0(N):
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

        def chooseCRange(N):
            def go(idx):
                if above:
                    return Range(1, N-idx)
                else:
                    return Range(-1*idx, 0)
            return Dep('c_idx0', go)

        memBound = heapSize if bof_instance.Location == 'HEAP' else stackSize

        # Excursion_Continuous => CONTINUOUS
        excursion = bof_instance.Excursion.split("_")[1].upper()
        pickDataRange(bof_instance.DataSize, memBound)

        self.PARAMS = {

            'N'                : pickDataRange(bof_instance.DataSize, memBound),
            'N2'               : pickDataRange(bof_instance.DataSize, memBound),

            # These should be set by 'magnitude'
            'idx0'             : Dep('N', chooseIdx0),
            'access_len'       : magRange,
            'incr'             : Dep('access_len', chooseIncr),

            'memmax'           : Choice(memBound),

            'buf_name'         : Name("buf", 3, 15),
            'buf_name2'        : Name("buf2", 3, 15),
            'tmp_var_name'     : Name("tmp", 3, 15),

            'excursion'        : Choice(excursion),
            'c_idx0'           : Dep('N', chooseCIdx0),
            'c_access_len'     : Dep('N', chooseCRange),
            'c_incr'           : Dep('c_access_len', chooseIncr),

            'buf_type'         : Choice(*C_TYPES),
            'buf_type2'        : Choice(*C_TYPES),
            'tmp_var_type'     : Choice(*C_TYPES),

            'buf_access'       : Choice(SCHEME[bof_instance.BufferIndexScheme]),
            'buf_cpy'          : Choice('LOOP'),# 'MEMCPY'),
            'relop'            : Choice('<=') if above else Choice('>='),
            'location'         : Choice(LOCATION[bof_instance.Location]),
            'read_write'       : Choice(ACCESS[bof_instance.Access]),
            'buf2'             : Choice('BUF2_PRESENT', 'BUF2_ABSENT'),
            'fun_bof_return'   : Choice('JMP', 'RETURN'),
        }
        read_after_write = ['NO_WRITE']
        try:
            if bof_instance.Access_Read_After_Write:
                read_after_write.append('READ_AFTER_WRITE')
        except:
            pass
        self.PARAMS['read_after_write'] = Choice(*read_after_write)

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

