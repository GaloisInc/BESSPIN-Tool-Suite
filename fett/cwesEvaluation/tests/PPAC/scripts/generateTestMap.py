#!/usr/bin/env python3
"""
This script generates a mapping from test names (for entry in a
configCWEs.ini file) and features that, if enabled, imply the corresponding
test should be enabled.
"""
import json
import os, glob
import sys

def main():
    src          = sys.argv[1]
    testmap = {}
    for t in glob.glob(f"{src}/*.c"):
        t = os.path.splitext(os.path.basename(t))[0]
        testmap[t] = [ f"PPAC_{t.lower()}" ]
    print(json.dumps(testmap))

if __name__ == "__main__":
    main()
