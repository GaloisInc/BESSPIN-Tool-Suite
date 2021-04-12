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
    cwesEvaluationDir = os.path.join(repoDir,"besspin","cwesEvaluation")

    # Import prettyVulClass
    sys.path.insert(0, repoDir)
    import besspin.base.config #To resolve cyclic importing
    from besspin.cwesEvaluation.scoreTests import prettyVulClass

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

    # Generate the document
    try:
        fDoc = open(os.path.join(repoDir,"docs","cwesEvaluation","BESSPIN-Coeffs.md"),"w")
        # Intro
        fDoc.write(
            "# BESSPIN Coefficients Values\n"
            "This file is automatically generated. Please do not edit.\n\n"
            "To generate, please use [this utility](../build/besspinCoeffsList.py).\n\n"
        )

        # Table Header
        fDoc.write(
            "| Vulnerability Class | Weakness Category | TI | AV | BI | LDX |\n"
            "|-|-|-|-|-|-|\n"
        )

        for vulClass in vulClasses:
            for xCategory,cData in besspinCoeffs[vulClass].items():
                fDoc.write(
                    f'|{prettyVulClass(vulClass)}'
                    f'|{cData["name"]}'
                    f'|{cData["factors"]["TI"]}'
                    f'|{cData["factors"]["AV"]}'
                    f'|{cData["factors"]["ENV"]["BI"]}'
                    f'|{cData["factors"]["ENV"]["LDX"]}'
                    '|\n'
                )
            # Class separator
            fDoc.write("|||||||\n")

        fDoc.close()
    except Exception as exc:
        errorExit(f"Failed to generate the document <BESSPIN-Coeffs.md>.",exc=exc)

    print("Document generated!")

def loadJsonFile (jsonFile):
    """
    Reads a json file and returns a dictionary with its data
    
    ARGUMENTS:
    ----------
    jsonFile: String
        Path to a json file

    RETURN:
    -------
    Dict
    """
    try:
        fJson = open(jsonFile, 'r')
        jsonData = json.load(fJson)
        fJson.close()
    except Exception as exc:
        errorExit(f"Failed to load json file <{jsonFile}>.",exc=exc)
    return jsonData

def formatExc (exc):
    """ format the exception for printing 
    
    ARGUMENTS:
    ----------
    exc: Exception
    
    RETURN:
    ------
    String: Either the text desription of the Exception, or 
                The <Non-recognized Exception> string.
    """
    try:
        return f"<{exc.__class__.__name__}>: {exc}"
    except:
        return '<Non-recognized Exception>'

def errorExit(message,exc=None):
    """
    Exits the utility and reports error

    ARGUMENTS:
    ----------
    message: String
        error message

    exc: Exception

    SIDE-EFFECTS:
    -------------
    - prints ERROR + error message + exception text if applicable
    - exits with code 1
    """
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