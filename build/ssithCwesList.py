#! /usr/bin/env python3

"""
This utility does the following:
    1. Check that all the following are synchronized:
        - The google spreadsheet (as csv: File->Download->csv[current sheet])
            > Checks that the list count is proper.
        - The ini files: test_
        - The ini files: assessment_
        - The setupEnv.json files (+ description)
        - Cfr files
    2. If the checks passed, generate the readme with the final CWEs list.
"""

"""
usage: ssithCwesList.py [-h] csvFile

Checks and synchronizes the SSITH CWEs list across the tool's components

positional arguments:
  csvFile     Path to the CSV of the google spreadsheet

optional arguments:
  -h, --help  show this help message and exit
"""

import sys, os, argparse, json, configparser

# Globals
cwesShortcuts = {
    "BOF" : "bufferErrors", 
    "PPAC" : "PPAC",
    "RM" : "resourceManagement",
    "IEX" : "informationLeakage",
    "NE" : "numericErrors",
    "SOC" : "hardwareSoC",
    "INJ" : "injection"
}
vulClasses = list(cwesShortcuts.values())
cwesCsvHeaders = {"vulClass" : 1, "CWE":2, "Link":3, "Description":4, "CWEs List":6, "# CWEs":7}

class cwesDict:
    def __init__(self, fPath):
        self.fPath = fPath
        self._cwes = {vulClass : [] for vulClass in vulClasses}
    
class cwesDictCSV(cwesDict):
    def __init__(self,fPath):
        super().__init__(fPath)
        self.loadedCount = {vulClass : 0 for vulClass in vulClasses} 

    def addCsvCwe(self,row):
        xCwe = csvRow(row)
        self._cwes[xCwe.vulClass].append(xCwe)
        if (xCwe.doesHaveCwesList):
            self.loadedCount[xCwe.cwesListVulClass] = xCwe.cwesListCount

    def checkSpreadsheetTotals(self):
        for vulClass in vulClasses:
            if (len(self._cwes[vulClass])==0):
                errorExit(f"No CWES found for <{vulClass}> in {self.fPath}.")
            if (self.loadedCount[vulClass]==0):
                errorExit(f"Failed to find the CWEs total count for <{vulClass}> in <{self.fPath}>.")
            if (len(self._cwes[vulClass]) != self.loadedCount[vulClass]):
                errorExit(f"Something is wrong in the spreadsheet totals in {self.fPath}. The CWEs total "
                    f"count(={self.loadedCount[vulClass]}) for <{vulClass}> does not match the actual "
                    f"number of CWE rows(={len(self._cwes[vulClass])}).")
        print("CHECK: Spreadsheet totals.")

class csvRow:
    def __init__(self, row):
        #Read the overall count list
        self.doesHaveCwesList = (row[cwesCsvHeaders["CWEs List"]] in cwesShortcuts)
        if (self.doesHaveCwesList):
            self.cwesListVulClass = cwesShortcuts[row[cwesCsvHeaders["CWEs List"]]]
            self.cwesListCount = int(row[cwesCsvHeaders["# CWEs"]])
        self.vulClass = cwesShortcuts[row[cwesCsvHeaders["vulClass"]]]
        self.description = row[cwesCsvHeaders["Description"]]

def formatExc (exc):
    """ format the exception for printing """
    try:
        return f"<{exc.__class__.__name__}>: {exc}"
    except:
        return '<Non-recognized Exception>'

def errorExit(message,exc=None):
    if (exc):
        message += f"\n{formatExc(exc)}."
    print(f"(ERROR)~ {message}")
    # Uncomment for traceback.
    #if (exc):
    #    print(traceback.format_exc())
    exit(1)

def loadCsvCwes(csvLines, fPath):
    csvCwes = cwesDictCSV(fPath);
    for line in csvLines:
        items = line.split(',')
        if (len(items)!=max(cwesCsvHeaders.values())+1):
            raise Exception(f"Invalid row <{line}>.")
        if (items[0] == "Class"): #this is the first line
            continue
        csvCwes.addCsvCwe(items)
    return csvCwes

def loadFile (fPath,fType):
    try:
        f = open(fPath, 'r')
        if (fType=="json"):
            ret = json.load(f)
        elif (fType=="csv"): #this is the CSV main file
            ret = loadCsvCwes(f.read().splitlines(), fPath)
        elif (fType=="ini"):
            ret = configparser.ConfigParser()
            ret.optionxform = str # Hack it to be case sensitive
            ret.read_file(f)
        else:
            raise Exception(f"Unknwon type <{fType}>")
        f.close()
    except Exception as exc:
        errorExit(f"Failed to load {fType} file <{fPath}>.",exc=exc)
    print(f"<{fPath}> was loaded successfully.")
    return ret


def main(xArgs):
    buildDir = os.path.abspath(os.path.dirname(__file__))
    repoDir = os.path.abspath(os.path.join(buildDir,os.pardir))

    # Load the google spreadsheet
    spreadsheetCWEs = loadFile(xArgs.csvFile,"csv")
    spreadsheetCWEs.checkSpreadsheetTotals()

    # Load the ini file 


if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Checks and synchronizes the SSITH CWEs list across the tool\'s components')
    xArgParser.add_argument('csvFile', help='Path to the CSV of the google spreadsheet')
    xArgs = xArgParser.parse_args()
    main(xArgs)