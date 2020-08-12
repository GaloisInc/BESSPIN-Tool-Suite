#!/usr/bin/env python
import os
import glob
import subprocess
import logging


LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)
logger = logging.getLogger(__name__)

def barename(x):
    return os.path.basename(os.path.splitext(x)[0])

def dirnames(pattern):
    return list(map(barename, glob.glob(pattern)))

def main():
    tests        = dirnames("./tests/*.c")
    stores       = dirnames("./stores/*.c")
    interpreters = dirnames("./interpreters/*.c")


    cwes = {}
    for source in glob.glob("./tests/*.c"):
        line = subprocess.run(['head', '-n', '1', source], capture_output=True).stdout.decode('utf-8')
        idx = line.find("CWE:")
        cwes[barename(source)] = line[idx+4:idx+7]

    found = []
    none = []

    for t in tests:
        for s in stores:
            for i in interpreters:
                makecmd = ["make", f'TEST={t}', f'STORE={s}', f'INTERPRETER={i}', 'weakness']
                logger.debug(f"Executing: <{makecmd}>");
                make = subprocess.run(makecmd, capture_output=True)
                output = make.stdout.decode('utf-8')
                logger.debug(f"make result: {output}")

                test = subprocess.run([f'./{t}.{s}.{i}.riscv'], capture_output=True)
                output = test.stdout.decode('utf-8')
                logger.debug(f"Test result: {output}")

                if test.stdout.find(b"TEST FAILED.") >= 0:
                    found.append((t,s,i))
                elif test.stdout.find(b"TEST PASSED.") >= 0:
                    none.append((t,s,i))
                else:
                    logger.debug(f"Error getting result of {t}:{s}:{i}")
                    exit(1)
                subprocess.run(["rm", f"{t}.{s}.{i}.riscv"])

    print("CWE,TEST,STORE,INTERPRETER,PASS")
    if len(found) > 0:
        for (t,s,i) in found:
            cwe = cwes[t]
            print(f"{cwe},{t},{s},{i},✗")
    if len(none) > 0:
        for (t,s,i) in none:
            cwe = cwes[t]
            print(f"{cwe},{t},{s},{i},✓")

if __name__ == "__main__":
    main()
