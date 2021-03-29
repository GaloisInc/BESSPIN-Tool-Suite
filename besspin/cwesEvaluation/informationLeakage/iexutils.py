import os
import glob

def barename(x):
    return os.path.basename(os.path.splitext(x)[0])

def dirnames(pattern):
    return list(map(barename, glob.glob(pattern)))

def exeName(t,s,i):
    return f"{t}_{s}_{i}.riscv"

