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

import sys, os, argparse, json, configparser, subprocess

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
exclusions = ( #These are not checked: fPath-vulClass
    [f"configSecurityTests-test-{vClass}" for vClass in ["bufferErrors", "informationLeakage"]]
    +
    [f"ClaferModel-{vClass}" for vClass in ["PPAC", "hardwareSoC", "injection"]]
    + 
    [f"{fPath}-injection" for fPath in ["configSecurityTests-test","configSecurityTests-assessment","setupEnv"]]
)

class cwesDict:
    def __init__(self, fPath):
        self.fPath = fPath
        self._cwes = {vulClass : {} for vulClass in vulClasses}

    def compare (self, target, checkDescription=False):
        for vulClass in vulClasses:
            if (f"{target.fPath}-{vulClass}" in exclusions):
                continue
            cwes1 = set(self._cwes[vulClass].keys())
            cwes2 = set(target._cwes[vulClass].keys())
            if (cwes1 == cwes2):
                if (checkDescription):
                    for xCwe in self._cwes[vulClass].values():
                        yCwe = target._cwes[vulClass][xCwe.id]
                        if (yCwe.description not in xCwe.description):
                            errorExit(f"MISMATCH! description of <{xCwe.id}> in [<{self.fPath}> ^ <{target.fPath}>] in <{vulClass}>.")
                continue
            else:
                errorExit(f"MISMATCH! <{self.fPath}> ^ <{target.fPath}> = {cwes1 ^ cwes2} in <{vulClass}>.")

        print(f"CHECK: <{self.fPath}> matches <{target.fPath}>.")

    def getVulClassCount(self, vulClass):
        return len(self._cwes[vulClass])

    def getCwesObjects(self, vulClass):
        return self._cwes[vulClass].values()

class cwesDictCFR(cwesDict):
    def __init__(self,fPath):
        super().__init__(fPath)

    def addVulClass(self,vulClass,vCfr):
        for xCwe in vCfr:
            cweNum = xCwe.split("CWE_")[-1]
            self._cwes[vulClass][cweNum] = cwe(vulClass,cweNum)


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
            self._cwes[vulClass][cweNum] = xCwe

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
        if (f"{self.fPath}-{vulClass}" in exclusions):
            return #ini is done differently for these classes
        if (not vConfig.has_section(configSection)):
            errorExit(f"Missing section <{configSection}> in <{self.fPath}> for <{vulClass}>.")

        for option in vConfig.options(configSection):
            if (option.startswith('_')): #That's a fake option
                continue
            cweNum = option.split(f"{sectionType}_")[-1]
            self._cwes[vulClass][cweNum] = cwe(vulClass,cweNum)

class cwesDictCSV(cwesDict):
    def __init__(self,fPath):
        super().__init__(fPath)
        self.loadedCount = {vulClass : 0 for vulClass in vulClasses} 

    def addCsvCwe(self,row):
        xCwe = csvRow(row)
        self._cwes[xCwe.vulClass][xCwe.id] = xCwe
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
        self.id = num.replace('-','_')

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
        elif (fType=="cfr"):
            cfrCmd = ["clafer", "-s", "-o", "-m", "fmjson", fPath]
            cfrData = json.loads(subprocess.check_output(cfrCmd,stderr=subprocess.STDOUT))
            ret = cfrData["features"]["CWE"]["children"]
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

    # Load the cfr files
    cfrCWEs = cwesDictCFR("ClaferModel")
    for vulClass in vulClasses:
        if (f"{cfrCWEs.fPath}-{vulClass}" in exclusions):
            continue #No clafer models for these vulClasses
        vCfrCWEs = loadFile(os.path.join(cwesEvaluationDir,vulClass, f"{vulClass[0].upper()}{vulClass[1:]}.cfr"),"cfr")
        cfrCWEs.addVulClass(vulClass,vCfrCWEs)

    #Synchronize (considering the google spreadsheet as the golden ref)
    #1. ini test
    spreadsheetCWEs.compare(testConfigCWEs)
    #2. ini assignment
    spreadsheetCWEs.compare(assessConfigCWEs)
    #3. setupEnv 
    spreadsheetCWEs.compare(setupEnvCWEs,checkDescription=True)
    #4. cfr
    spreadsheetCWEs.compare(cfrCWEs)

    # Generate the README
    try:
        fReadme = open(os.path.join(repoDir,"docs","ssithCWEsList.md"),"w")
        # Intro
        fReadme.write(
            "# SSITH CWEs List\n"
            "This file is automatically generated. Please do not edit.\n\n"
            "To generate, please download a `.csv` version of the `Final List` sheet of the "
            "[Phase 3 CWEs Agreement](https://docs.google.com/spreadsheets/d/1xFl9oFcYGb6rLQpCbqQ_AiOPXq3P1GJKk5FxiY1o6XQ/edit#gid=1605695275) "
            "spreadsheet, and use [this utility](../build/ssithCWEsList.py).\n\n"
        )

        # Totals Table
        fReadme.write(
            "## Totals Summary\n"
            "---\n"
            "| Vulnerability Classes | # of CWEs |\n"
            "|-|-|\n"
        )
        for vulClass in vulClasses:
            fReadme.write(f"| {vulClass} | {spreadsheetCWEs.getVulClassCount(vulClass)} |\n")

        # CWEs list
        cwelink = "https://cwe.mitre.org/data/definitions/"
        for vulClass in vulClasses:
            fReadme.write(
                f"## {vulClass}\n"
                "---\n"
                "| CWE | Description |\n"
                "|-|-|\n"
            )
            for xCwe in spreadsheetCWEs.getCwesObjects(vulClass):
                try:
                    intVal = int(xCwe.id)
                    name = xCwe.id
                    link = f"{cwelink}{xCwe.id}"
                except: #custom CWE
                    name = xCwe.id.replace('_','-')
                    link = f"../fett/cwesEvaluation/{vulClass}/README.md"
                fReadme.write(f"| [CWE-{name}]({link}) | {xCwe.description} |\n")

        fReadme.close()
    except Exception as exc:
        errorExit(f"Failed to generate the readme file <ssithCWEsList.md>.",exc=exc)

    print("Readme generated!")

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Checks and synchronizes the SSITH CWEs list across the tool\'s components')
    xArgParser.add_argument('csvFile', help='Path to the CSV of the google spreadsheet')
    xArgs = xArgParser.parse_args()
    main(xArgs)