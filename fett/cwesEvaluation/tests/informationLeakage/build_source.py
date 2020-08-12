#!/usr/bin/env python3

import sys
import os

def main():
    name = sys.argv[1]
    base = os.path.splitext(os.path.basename(name))[0].split("_")[1:]
    print("informationLeakage/tests/{0}.c informationLeakage/stores/{1}.c informationLeakage/interpreters/{2}.c".format(base[0], base[1], base[2]))

if __name__ == "__main__":
    main()
