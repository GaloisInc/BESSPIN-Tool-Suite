#!/usr/bin/env python3
import os
import glob

from fett.base.utils.misc import *
from fett.cwesEvaluation.common import isTestEnabled
from fett.cwesEvaluation.tests.informationLeakage.iexutils import dirnames

def generateWrappers():
    src = os.path.join(getSetting('buildDir'), 'informationLeakage')

    tests        = dirnames(os.path.join(src, "tests", "*.c"))
    stores       = dirnames(os.path.join(src, "stores", "*.c"))
    interpreters = dirnames(os.path.join(src, "interpreters", "*.c"))

    nFiles = 0
    for t in tests:
        for s in stores:
            for i in interpreters:
                fileName = f"test_{t}_{s}_{i}.c"
                if isTestEnabled('informationLeakage', fileName):
                    nFiles += 1
                    fd = ftOpenFile(os.path.join(src, fileName), "w")
                    fd.write('#include <stdio.h>\n')
                    fd.write('int main()\n')
                    fd.write('{\n')
                    fd.write('\treturn test_main();\n')
                    fd.write('}\n')
                    fd.close()

    return nFiles

