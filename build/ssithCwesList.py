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

class cwesDictJSON(cwesDict):
    def __init__(self,fPath):
        super().__init__(fPath)

    def addVulClass(self,vulClass,vJson):
        vDict = vJson
        if (vulClass not in vDict):
            errorExit(f"Missing key <{vulClass}> in <{self.fPath}> for <{vulClass}>.")
        vDict = vDict[vulClass]
        foundTestsInfo = False
        for xContents in vDict:
            if (("name" in xContents) and (xContents["name"] == "testsInfo")):
                vDict = xContents["val"]
                foundTestsInfo = True
                break
        if (not foundTestsInfo):
            errorExit(f"Missing key <testsInfo> in <{self.fPath}> for <{vulClass}>.")
        for xTest,xItems in vDict.items():
            cweNum = xTest.split("test_")[-1]
            xCwe = cwe(vulClass,cweNum)
            if ("cweText" not in xItems):
                errorExit(f"Missing key <cweText> in <{self.fPath}> for <{vulClass}:{xTest}>.")
            xCwe.description = xItems["cweText"]
            self._cwes[vulClass].append(xCwe)

class cwesDictINI(cwesDict):
    def __init__(self,fPath):
        super().__init__(fPath)

    def addVulClass(self,vulClass,vConfig,sectionType):
        if (sectionType=="test"):
            configSection = "enabledTests"
        elif (sectionType=="assessment"):
            configSection = "selfAssessment"
        else:
            errorExit(f"addVulClass: called with the wrong sectionType <{sectionType}>.")

        if ((vulClass in ["bufferErrors", "informationLeakage"]) and (sectionType=="test")):
            return #Test selection is done differently for those classes
        if (not vConfig.has_section(configSection)):
            errorExit(f"Missing section <{configSection}> in <{self.fPath}> for <{vulClass}>.")

        for option in vConfig.options(configSection):
            if (option.startswith('_')): #That's a fake option
                continue
            cweNum = option.split(f"{sectionType}_")[-1]
            self._cwes[vulClass].append(cwe(vulClass,cweNum))

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

class cwe:
    def __init__(self,vulClass,num):
        self.vulClass = vulClass
        self.id = num

class csvRow(cwe):
    def __init__(self, row):
        #Read the overall count list
        self.doesHaveCwesList = (row[cwesCsvHeaders["CWEs List"]] in cwesShortcuts)
        if (self.doesHaveCwesList):
            self.cwesListVulClass = cwesShortcuts[row[cwesCsvHeaders["CWEs List"]]]
            self.cwesListCount = int(row[cwesCsvHeaders["# CWEs"]])
        self.description = row[cwesCsvHeaders["Description"]]
        vulClass = cwesShortcuts[row[cwesCsvHeaders["vulClass"]]]
        num = row[cwesCsvHeaders["CWE"]].split("CWE-")[-1]
        super().__init__(vulClass,num)

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

    # Load the config ini files
    testConfigCWEs = cwesDictINI("configSecurityTests-test")
    assessConfigCWEs = cwesDictINI("configSecurityTests-assessment")
    configCWEsDir = os.path.join(repoDir,"configSecurityTests")
    for vulClass in vulClasses:
        vConfig = loadFile(os.path.join(configCWEsDir,f"{vulClass}.ini"),"ini")
        testConfigCWEs.addVulClass(vulClass,vConfig,"test")
        assessConfigCWEs.addVulClass(vulClass,vConfig,"assessment")

    # Load the setupEnv files
    cwesEvaluationDir = os.path.join(repoDir,"fett","cwesEvaluation")
    setupEnvCWEs = cwesDictJSON("setupEnv")
    for vulClass in vulClasses:
        vJson = loadFile(os.path.join(cwesEvaluationDir,vulClass, "setupEnv.json"),"json")
        setupEnvCWEs.addVulClass(vulClass,vJson)


if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Checks and synchronizes the SSITH CWEs list across the tool\'s components')
    xArgParser.add_argument('csvFile', help='Path to the CSV of the google spreadsheet')
    xArgs = xArgParser.parse_args()
    main(xArgs)