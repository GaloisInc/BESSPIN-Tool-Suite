#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file configures a configCWEs.ini file.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import argparse
import configparser


def main (xArgs):
	#reading configuration file
    xConfig = configparser.ConfigParser()
    try:
        xConfig.optionxform = str # Hack it to be case sensitive
        xConfig.read(xArgs.file)
    except:
        print("Error in reading configuration file <{0}>. Please check its syntax.".format(xArgs.file))
        exit(1)

    #default section or chosen section
    xSection = 'enabledTests'
    if (xArgs.section):
        xSection = xArgs.section
    if (not xConfig.has_section(xSection)):
        print ("Error in <{0}>: Section <{1}> not found!.".format(xArgs.file,xSection))
        exit (1)

    def applyOption (cwe):
        if (xArgs.enable):
            xConfig.set(xSection,cwe,'Yes')
        elif (xArgs.disable):
            xConfig.set(xSection,cwe,'No')
        elif (xArgs.toggle):
            val = xConfig.getboolean(xSection,cwe)
            if (val):
                xConfig.set(xSection,cwe,'No')
            else:
                xConfig.set(xSection,cwe,'Yes')

    #changing the configuration as instructed
    if (xArgs.single): #only a single CWE
        cwe = "test_" + xArgs.single
        if (xConfig.has_option(xSection,cwe)):
            applyOption (cwe)
        else:
            print ("Error in <{0}>: CWE <{1}> not found!.".format(xArgs.file,cwe))
            exit (1)
    else: #all of them
        for cwe in xConfig.options(xSection):
            applyOption (cwe)

    #Writing the changed configuration file
    try:
        fConfig = open(xArgs.file,'w')
    except:
        print("Error: Cannot open configuration file <{0}> for writing.".format(xArgs.file))
        exit(1)
    xConfig.write(fConfig,space_around_delimiters=True)
    fConfig.close()

if __name__ == '__main__':
    #Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='configures a configCWEs')
    
    xGroupEnable = xArgParser.add_mutually_exclusive_group(required=True)
    xGroupEnable.add_argument ('-E', '--enable', help="enables all CWEs in the chosen config File.", action="store_true")
    xGroupEnable.add_argument ('-D', '--disable', help="disables all CWEs in the chosen config File.", action="store_true")
    xGroupEnable.add_argument ('-T', '--toggle', help="toggles all CWEs in the chosen config File.", action="store_true")
    xArgParser.add_argument ('-f', '--file', help="The chosen CWEs configuration file.", required=True)
    xArgParser.add_argument ('-cwe', '--single', help="Only apply to this CWE")
    xArgParser.add_argument ('-s', '--section', help="Section name")
    xArgs = xArgParser.parse_args()
    main(xArgs)