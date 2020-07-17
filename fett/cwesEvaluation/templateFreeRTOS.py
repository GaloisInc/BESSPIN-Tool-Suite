#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file generates the C template of "main_testgen.c" for FreeRTOS
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import sys, os
import re
import copy

def printAndReport (message,doExit=False):
    print (message)
    if (reportFile is not None):
        reportFile.write('\n' + message.rstrip() + '\n')
    if (doExit):
        exit (1)

def renameMain (testsDir,cTest):
    try:
        ftest = open("{0}/{1}".format(testsDir,cTest), "r")
        lines = ftest.read().splitlines()
        ftest.close()
    except:
        printAndReport ("Error in {0}: Failed to open <{1}/{2}> for reading.".format(fileName,testsDir,cTest),doExit=True)
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
        printAndReport ("Error in {0}: Failed to find the declaration in <{1}/{2}>.".format(fileName,testsDir,cTest),doExit=True)
    #1. change the file
    testName = cTest.split('.')[0]
    lines[declIndex] = "{0} main_{1} {2} {3}".format(declParts[0],testName,*declParts[1:])
    try:
        ftest = open("{0}/{1}".format(testsDir,cTest), "w")
        ftest.write('\n'.join(lines))
        ftest.close()
    except:
        printAndReport ("Error in {0}: Failed to open <{1}/{2}> for writing.".format(fileName,testsDir,cTest),doExit=True)
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
            except:
                printAndReport ("Error in {0}: Failed to open <{1}/main_{2}.c> for writing.".format(fileName,testsDir,testName),doExit=True)
            fmain.write("// This file is generated automatically by testgen\n\n")
            #standard includes
            fmain.write("#include <stdio.h>\n#include <string.h>\n#include <unistd.h>\n\n")
            #Declarations
            fmain.write("\nvoid main_testgen (void);\n\n")
            fmain.write("extern {0};\n".format(mainDeclaration))
            #The main function
            fmain.write("\n\nvoid main_testgen (void)\n{\n")
            fmain.write("\tprintf (\">>>Beginning of Testgen<<<\\n\");\n\n")
            fmain.write("\tmain_{0} ();\n".format(testName))
            fmain.write("\n\tprintf (\">>>End of Testgen<<<\\n\");\n}\n")
            fmain.close()

if __name__ == '__main__':
    fileName = os.path.basename(__file__)
    if ((len(sys.argv) == 3) and (os.path.isdir(sys.argv[1]))):
        try:
            reportFile = open(sys.argv[2],"a")
        except:
            print ("Warning in {0}: Failed to open report file. {0} will only print on screen.".format(fileName))
            reportFile = None
        main (sys.argv[1])
    else:
        print ("Error in {0}: Invalid arguments.".format(fileName))
        exit (1)