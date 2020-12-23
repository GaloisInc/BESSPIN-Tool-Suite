"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file generates the C template of "main_testgen.c" for FreeRTOS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import sys, os
import re
import copy

from fett.base.utils.misc import *

def renameMain (testsDir,cTest):
    lines = ftReadLines(f"{testsDir}/{cTest}")
    (declMatch, declIndex) = matchExprInLines(r'^\s*(?P<retType>void|int)\s+main\s*(?P<args>\([^)]*\))\s*(?P<brace>\{?)\s*', lines, returnIndex=True)
    if (not declIndex):
        logAndExit("<templateFreeRTOS>: Failed to find the declaration in <{0}/{1}>.".format(testsDir,cTest))
    declParts = [declMatch.group('retType'),declMatch.group('args'),declMatch.group('brace')]
    #1. change the file
    testName = cTest.split('.')[0]
    lines[declIndex] = "{0} main_{1} {2} {3}".format(declParts[0],testName,*declParts[1:])
    try:
        ftest = ftOpenFile("{0}/{1}".format(testsDir,cTest), "w")
        ftest.write('\n'.join(lines))
        ftest.close()
    except Exception as exc:
        logAndExit("<templateFreeRTOS>: Failed to open <{0}/{1}> for writing.".format(testsDir,cTest),exc=exc)
    #2. return the declaration
    return "{0} main_{1} {2}".format(declParts[0],testName,declParts[1])


def templateFreeRTOS(testsDir):
    #Load the template 
    testTemplate = ftReadLines(getSetting("cweTestTemplateFreeRTOS"),splitLines=False)

    #For each file: rename main + Generating the main_testgen wrapper
    for srcTest in sorted(os.listdir(testsDir)):
        if (srcTest.endswith(".c")):
            testName = srcTest.split('.')[0]
            mainDeclaration = renameMain(testsDir,srcTest)
            #Customize the template
            testLines = testTemplate.replace("MAIN_DECLARATION",mainDeclaration)
            testLines = testLines.replace("TEST_NAME",testName)
            #Write the test
            fmain = ftOpenFile("{0}/main_{1}.c".format(testsDir,testName), "w")
            fmain.write(testLines)
            fmain.close()
