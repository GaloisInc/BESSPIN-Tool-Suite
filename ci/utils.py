#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- This files provides some utility functions
"""

from configs import *
import configparser, os, copy

def exitFettCi (exitCode=-1,exc=None,message=None):
    if (message):
        print(f"(Error)~  FETT-CI: {message}")
    if (exc):
        print(f"(Error)~  <{exc.__class__.__name__}>: {exc}")
    if (exitCode == -1):
        print(f"(FATAL)~  End of FETT-CI: <JOB-FAILURE>")
    elif (exitCode == 0):
        print(f"(Info)~  End of FETT-CI: <JOB-SUCCESS>")
    else:
        print(f"(Info)~  End of FETT-CI: <JOB-FAILURE>")
    exit(exitCode)

def exitOnInterrupt (xSig,xFrame):
    signalNames = {2:'SIGINT', 15:'SIGTERM', 5:'SIGTRAP', 6:'SIGABRT'}
    if (xSig in signalNames):
        sigName = signalNames[xSig]
    else:
        sigName = f"signal#{xSig}"
    exitFettCi(message=f"Received <{sigName}>!")

def generateAllConfigs():
    #create a list of unique dictionaries. Each dictionary can become a .ini instance
    def createConfig (inputSet, inputDict):
        if (not inputSet): #we're done
            return

        newSetting = inputSet.pop()
        settingName = newSetting[0]
        values = list(newSetting[1])
        
        #Create a new set/dict for every extra value
        for iValue in values[1:]:
            newDict = copy.deepcopy(inputDict)
            allConfigs.append(newDict)
            newDict[settingName] = iValue
            newDict['name'] += [str(iValue)]
            newSet = copy.deepcopy(inputSet)
            createConfig (newSet, newDict)

        #Keep the inputDict for values[0]
        if (len(values) > 1):
            inputDict['name'] += [str(values[0])]
        inputDict[settingName] = values[0]
        createConfig (inputSet, inputDict)
        
    allConfigs = []

    for xApp,xSet in appSets.items():
        inputSet = copy.deepcopy(xSet)
        inputDict = {'name': [xApp]}
        allConfigs.append(inputDict)
        createConfig (inputSet, inputDict)

    #Produce a consistent naming order:
    for xConfig in allConfigs:
        xConfig['name'] = '_'.join(sorted(xConfig['name'])) #sort the name components, then join them with '_'
    allConfigs.sort(key = lambda item: item['name']) #sort the list based on item['name']
    
    return allConfigs

def generateConfigFile (repoDir,dictConfig,testMode):
    #loading the template configuration file (the repo's default)
    templateConfigPath = os.path.join(repoDir,'config.ini')
    xConfig = configparser.ConfigParser()
    try:
        fConfig = open(templateConfigPath,'r')
        xConfig.read_file(fConfig)
        fConfig.close()
    except Exception as exc:
        exitFettCi(message=f"Failed to read configuration file <{templateConfigPath}>.",exc=exc)

    #Adjusting the xConfig
    fileName = None
    for xSetting, xValue in dictConfig.items():
        wasSet = False
        if (xSetting == 'name'):
            fileName = f"{xValue}.ini"
            continue
        for xSection in xConfig:
            if (xSetting in xConfig[xSection]):
                xConfig.set(xSection,xSetting,str(xValue))
                wasSet = True
                break
        if (not wasSet):
            exitFettCi(message=f"Failed to find the setting <{xSetting}> in <{templateConfigPath}>.")
    if (not fileName):
        exitFettCi(message=f"Failed to find the key <name> in dictConfig.")

    #Creating the config file
    if (testMode):
        dumpDir = os.path.join(repoDir,'dumpIni')
        xConfigFilePath = os.path.join(dumpDir,fileName)
        print(f"\t{fileName}")
    else:
        xConfigFilePath = os.path.join(repoDir,fileName)

    try:
        fConfig = open(xConfigFilePath,'w')
        xConfig.write(fConfig)
        fConfig.close()
    except Exception as exc:
        exitFettCi(message=f"Failed to write configuration file <{xConfigFilePath}>.",exc=exc)

    return xConfigFilePath

def prepareArtifact(configFile,artifactSuffix):
    #path to the artifact folder
    pass




