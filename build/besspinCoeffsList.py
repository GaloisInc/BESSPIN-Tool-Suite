#! /usr/bin/env python3

"""
This utility does the following:
    1. Checks that <besspinCoeffs.json> covers ALL the CWEs (fetched from the vulClass/setupEnv.json)
    2. Generates the markdown document with the BESSPIN Coeffs list in a perttier format than json.
"""

import sys, os, argparse, json

vulClasses = [ "bufferErrors", "PPAC", "resourceManagement", "informationLeakage", "numericErrors", "hardwareSoC", "injection" ]

def main(xArgs):
    buildDir = os.path.abspath(os.path.dirname(__file__))
    repoDir = os.path.abspath(os.path.join(buildDir,os.pardir))
    cwesEvaluationDir = os.path.join(repoDir,"fett","cwesEvaluation")

    # Load the besspinCoeffs file
    besspinCoeffs = loadJsonFile(os.path.join(cwesEvaluationDir,"utils","besspinCoeffs.json"))

    # Load the setupEnv files
    toolCWEs = {vulClass:[] for vulClass in vulClasses}
    for vulClass in vulClasses:
        setupEnvData = loadJsonFile(os.path.join(cwesEvaluationDir,vulClass, "setupEnv.json"))
        testsDict = None
        if (vulClass in setupEnvData):
            for xDict in setupEnvData[vulClass]:
                if (("name" in xDict) and (xDict["name"]=="testsInfo") and ("val" in xDict)):
                    testsDict = xDict["val"]
        if (testsDict is None):
            errorExit(f"Failed to extract the tests dict in <{vulClass}/setupEnv.json>.")
        for xTest in testsDict.keys():
            if (not xTest.startswith("test_")):
                errorExit(f"Unrecognized test format in <{vulClass}/setupEnv.json>: <{xTest}>.")
            toolCWEs[vulClass].append(xTest.split("test_")[1])

    # Check for the complete coverage
    for vulClass in vulClasses:
        # Get CWEs from besspinCoeffs
        vBesspinCoeffsCWEs = set()
        if (vulClass not in besspinCoeffs):
            errorExit(f"<besspinCoeffs.json> is missing <{vulClass}>.")
        for xCategory,cData in besspinCoeffs[vulClass].items():
            if ("cwes" not in cData):
                errorExit(f"<{vulClass}:{xCategory}> in <besspinCoeffs.json> is missing <cwes>.")
            vBesspinCoeffsCWEs.update(set(cData["cwes"]))
        # Compare
        if (vBesspinCoeffsCWEs != set(toolCWEs[vulClass])):
            errorExit(f"MISMATCH! <besspinEnv> ^ <setupEnv.json> = {vBesspinCoeffsCWEs ^ set(toolCWEs[vulClass])} in <{vulClass}>.")
    print("CHECK: The CWEs in <besspinCoeffs.json> completely cover the CWEs in <${{vulClass}}/setupEnv.json>.")

def loadJsonFile (jsonFile):
    try:
        fJson = open(jsonFile, 'r')
        jsonData = json.load(fJson)
        fJson.close()
    except Exception as exc:
        errorExit(f"Failed to load json file <{jsonFile}>.",exc=exc)
    return jsonData

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
    #    import traceback
    #    print(traceback.format_exc())
    exit(1)

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Checks the BESSPIN coeffs CWEs coverage and updates the pretty document.')
    xArgs = xArgParser.parse_args()
    main(xArgs)