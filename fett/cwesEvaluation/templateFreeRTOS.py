"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file generates the C template of "main_testgen.c" for FreeRTOS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import sys, os
import re
import copy

from fett.base.utils.misc import *

def renameMain (testsDir,cTest):
    try:
        ftest = open("{0}/{1}".format(testsDir,cTest), "r")
        lines = ftest.read().splitlines()
        ftest.close()
    except Exception as exc:
        logAndExit("<templateFreeRTOS>: Failed to open <{0}/{1}> for reading.".format(testsDir,cTest), exc=exc)
    declIndex = False
    declComponents = []
    for index,line in enumerate(lines):
        declMatch = re.match(r'^\s*(?P<retType>void|int)\s+main\s*(?P<args>\([^)]*\))\s*(?P<brace>\{?)\s*',line)
        #sed -E -i "s/^\s*(void|int)\s+(\w+)\s*(\([^)]*\))\s*(\{?)\s*/\1 \2_$testName \3 \4/" $cTest
        if (declMatch is not None):
            declIndex = index
            declParts = [declMatch.group('retType'),declMatch.group('args'),declMatch.group('brace')]
            break
    if (not declIndex):
        logAndExit("<templateFreeRTOS>: Failed to find the declaration in <{0}/{1}>.".format(testsDir,cTest))
    #1. change the file
    testName = cTest.split('.')[0]
    lines[declIndex] = "{0} main_{1} {2} {3}".format(declParts[0],testName,*declParts[1:])
    try:
        ftest = open("{0}/{1}".format(testsDir,cTest), "w")
        ftest.write('\n'.join(lines))
        ftest.close()
    except Exception as exc:
        logAndExit("<templateFreeRTOS>: Failed to open <{0}/{1}> for writing.".format(testsDir,cTest),exc=exc)
    #2. return the declaration
    return "{0} main_{1} {2}".format(declParts[0],testName,declParts[1])


def main (testsDir):
    #For each file: rename main + Generating the main_testgen wrapper
    for srcTest in sorted(os.listdir(testsDir)):
        if (srcTest.endswith(".c")):
            testName = srcTest.split('.')[0]
            mainDeclaration = renameMain(testsDir,srcTest)
            try:
                fmain = open("{0}/main_{1}.c".format(testsDir,testName), "w")
            except Exception as exc:
                logAndExit("<templateFreeRTOS>: Failed to open <{0}/main_{1}.c> for writing.".format(testsDir,testName), exc=exc)
            fmain.write("// This file is generated automatically by testgen\n\n")
            #standard includes
            fmain.write("#include <stdio.h>\n#include <string.h>\n#include <unistd.h>\n\n")
            # Include fettFreeRTOS.h
            # TODO: The compiler complains if we dont include this, but do we
            # *actually* need it?  It defines xMainTask, which we also don't
            # use but need for Include fettFreeRTOS.h for compilati
            # TODO: The compiler complains if we dont include this, but do we
            # *actually* need it?  It defines xMainTask, which we also don't
            # use but need for fettNtk.c.  Do we even need that?  It feels like
            # this build could be streamlined as we don't need all of the fett
            # stuff
            fmain.write('\n#include "fettFreeRTOS.h"\n\n')

            #Declarations
            fmain.write("\nvoid main_fett (void);\n\n")
            fmain.write("extern {0};\n".format(mainDeclaration))

            # Dummy xMainTask
            # TODO: I needed this for compilation, but it seems pretty
            # unnecessary
            fmain.write("\nTaskHandle_t xMainTask = NULL;\n\n")

            #The main function
            fmain.write("\n\nvoid main_fett (void)\n{\n")
            fmain.write("\tprintf (\">>>Beginning of Fett<<<\\n\");\n\n")
            fmain.write("\tmain_{0} ();\n".format(testName))
            fmain.write("\n\tprintf (\">>>End of Fett<<<\\n\");\n}\n")
            fmain.close()
