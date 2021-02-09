#!/usr/bin/env python3
import os
import glob

from fett.base.utils.misc import *
from fett.cwesEvaluation.common import isTestEnabled
from fett.cwesEvaluation.informationLeakage.iexutils import dirnames

def generateWrappers():
    src = os.path.join(getSetting('buildDir'), 'informationLeakage')
    enabledDrivers = set()
    enabledBins = []

    # Nonstandard tests
    nonStdDir = os.path.join(src, "nonstandard")
    tests = dirnames(os.path.join(nonStdDir, "*.c"))
    for t in tests:
        if (isTestEnabled('informationLeakage',t)):
            enabledDrivers.add(t.split("test_")[-1])
            enabledBins.append(f"{t}.riscv")
            # In unix this file will avoid "crossCompileUnix" skipping, and will be used by FreeRTOS
            cp (os.path.join(nonStdDir,f"{t}.c"),src) 
        else: #delete the file
            try:
                os.remove(os.path.join(nonStdDir, f"{t}.c"))
            except Exception as exc:
                logAndExit(f"generateWrappers for IEX: Failed to delete the file <{os.path.join(nonStdDir, f'{t}.c')}>",
                    exc=exc,exitCode=EXIT.Files_and_paths)

    # Standard tests
    tests        = dirnames(os.path.join(src, "tests", "*.c"))
    stores       = dirnames(os.path.join(src, "stores", "*.c"))
    interpreters = dirnames(os.path.join(src, "interpreters", "*.c"))

    for t in tests:
        for s in stores:
            for i in interpreters:
                fileName = f"test_{t}_{s}_{i}.c"
                # Skip the not-implemented tests
                if ((t == "cache") and (s != "cached")):
                    printAndLog(f"generateWrappers: Skipping {fileName}. It is not implemented.",doPrint=False)
                    continue
                if ((t == "setenv") and isEqSetting('osImage','FreeRTOS')):
                    printAndLog(f"generateWrappers: Skipping {fileName}. It is not implemented on FreeRTOS.",doPrint=False)
                    continue
                if isTestEnabled('informationLeakage', fileName.split(".c")[0]):
                    enabledDrivers.add(t)
                    enabledBins.append(fileName.replace(".c",".riscv"))
                    fd = ftOpenFile(os.path.join(src, fileName), "w")
                    fd.write('#include <stdio.h>\n')
                    fd.write('int main()\n')
                    fd.write('{\n')
                    fd.write('\treturn test_main();\n')
                    fd.write('}\n')
                    fd.close()

    return (enabledDrivers, enabledBins)

