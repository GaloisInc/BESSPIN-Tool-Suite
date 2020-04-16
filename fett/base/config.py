#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file parses the input configuration ini file, checks its legality, and stores all the settings.
json details are in: ./utils/configData.json
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import configparser, json, os, re
from fett.base.utils.misc import *

CONFIG_SECTIONS = ['backend', 'applications', 'build']
APPS = {'FreeRTOS' : ['https', 'ota'], 'debian' : ['webserver', 'database'], 'FreeBSD' : ['webserver', 'database']}

def loadJsonFile (jsonFile):
    try:
        fJson = open(jsonFile,'r')
        jsonData = json.load(fJson)
        fJson.close()
    except Exception as exc:
        logAndExit(f"Failed to load json file <{jsonFile}>.",exc=exc)
    return jsonData

@decorate.debugWrap
def loadConfiguration(configFile):
    #loading dev setup environment
    baseDir = os.path.abspath(os.path.dirname(__file__))
    fettDir = os.path.abspath(os.path.join(baseDir, os.pardir))
    setSetting('fettDir',fettDir)
    setupEnvFile = os.path.join(baseDir,'utils','setupEnv.json')
    setupEnvData = loadJsonFile(setupEnvFile)
    loadConfigSection(None,setupEnvData,'setupEnv',setup=True)

    #loading the configuration file
    xConfig = configparser.ConfigParser()
    try:
        fConfig = open(configFile,'r')
        xConfig.read_file(fConfig)
        fConfig.close()
    except Exception as exc:
        logAndExit(f"Failed to read configuration file <{configFile}>.",exc=exc)

    #loading the configuration parameters data
    configDataFile = getSetting('jsonDataFile')
    configData = loadJsonFile(configDataFile)

    # Here we should read the options and such
    for xSection in CONFIG_SECTIONS:
        loadConfigSection (xConfig,configData,xSection)

    printAndLog('Configuration loaded successfully.')
    return

@decorate.debugWrap
def loadConfigSection (xConfig, jsonData,xSection,setup=False):
    if (setup):
        fileName = "SetupEnv file"
    else:
        fileName = "Configuration file"

    if (not setup):
        try:
            assert xConfig.has_section(xSection)
        except Exception as exc:
            logAndExit(f"Section <{xSection}> not found in configuration file.",exc=exc)
        optionsInConfig = dict.fromkeys(xConfig.options(xSection),False) #to see if some unwanted parameters in config file
    
    try:
        jsonPars = jsonData[xSection]
    except Exception as exc:
        logAndExit(f"Section <{xSection}> not found in json configuration info file.",exc=exc)

    for iPar in jsonPars:
        if (('name' not in iPar) or ('type' not in iPar)):
            logAndExit("While reading json configuration info file. <%s> is missing a <name> or <type> in section [%s]." %(iPar['name'],xSection))
        #checking the value types + fetching the values--------------
        if (setup):
            if ('val' not in iPar):
                logAndExit(f"While reading json setupEnv file. <{iPar['name']}> is missing <val>.")
        else:
            try:
                assert xConfig.has_option(xSection,iPar['name'])
            except Exception as exc:
                logAndExit(f"{fileName}: <{iPar['name']}> not found in section [{xSection}].",exc=exc)
            optionsInConfig[iPar['name'].lower()] = True #Be careful! configparser options are always case insensitive and are all lowercase
        
        if (iPar['type'] in 'integer'): #works for int or integer
            try:
                if (setup):
                    val = int(iPar['val'])
                else:
                    val = xConfig.getint(xSection,iPar['name'])
            except Exception as exc:
                logAndExit(f"{fileName}: <{iPar['name']}> has to be integer in section [{xSection}].",exc=exc)
        elif (iPar['type'] in 'boolean'): #works for bool or boolean
            try:
                if (setup):
                    val = bool(int(iPar['val']))
                else:
                    val = xConfig.getboolean(xSection,iPar['name'])
            except Exception as exc:
                logAndExit(f"{fileName}: <{iPar['name']}> has to be boolean in section [{xSection}].",exc=exc)
        elif ( iPar['type'] in ['str', 'string', 'filePath', 'dirPath', 'ipAddress']):
            if (setup):
                val = iPar['val']
            else:
                val = xConfig.get(xSection,iPar['name'])
            if (len(val)==0):
                logAndExit(f"{fileName}: Failed to read <{iPar['name']}> in section [{xSection}]. Is it empty?")
            if ('#' in val):
                logAndExit(f"{fileName}: Illegal character in <{iPar['name']}> in section [{xSection}]. Is there a comment next to the value?")
            if (iPar['type'] == 'filePath'):
                doCheckPath = True
                if (setup):
                    val = os.path.join(getSetting('fettDir'),val)
                if (not setup and ('condition' in iPar)): #skip checking the path if the setting is disabled
                    if (xConfig.has_option(xSection,iPar['condition'])):
                        try:
                            doCheckPath = xConfig.getboolean(xSection,iPar['condition'])
                        except Exception as exc:
                            logAndExit("Configuration file: <%s> has to be boolean in section [%s]." %(iPar['condition'],xSection),exc=exc)
                    else:
                        logAndExit(f"Configuration file: The condition <{iPar['condition']}> is not found in section [{xSection}].")
                elif (setup and ('condition' in iPar)):
                    logAndExit (f"The <condition> option is not yet implemented for the setupEnv json.")
                if (doCheckPath and (not os.path.isfile(val))):
                    logAndExit(f"{fileName}: <{iPar['name']}> has to be a valid file path in section [{xSection}].")
            elif (iPar['type'] == 'dirPath'):
                if (setup):
                    val = os.path.join(getSetting('fettDir'),val)
                if (not os.path.isdir(val)):
                    logAndExit(f"{fileName}: <{iPar['name']}> has to be a valid directory path in section [{xSection}].")
            elif (iPar['type'] == 'ipAddress'):
                ipMatch = re.match(r"(\d{1,3}\.){3}\d{1,3}$",val)
                if (ipMatch is None):
                    logAndExit(f"{fileName}: <{iPar['name']}> has to be a valid IP address in section [{xSection}].")
        else:
            logAndExit("Json info file: Unknown type <%s> for <%s> in section [%s]." %(iPar['type'],iPar['name'],xSection))

        #checking the values choices + limits
        isChoices= False
        isMin = False
        isMax = False
        if ('choices' in iPar):
            if ( (iPar['type'] not in 'string') and (iPar['type'] not in 'integer') ):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <choices> for type <%s>." %(iPar['name'],xSection,iPar['type']))
            else: #int, str, stringsList
                isChoices = True
        if ('min' in iPar):
            if ( (iPar['type'] not in 'integer') and ('hex' not in iPar['type']) ):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <min> for type <%s>." %(iPar['name'],xSection,iPar['type']))
            elif ( isChoices and (iPar['type'] in 'integer')):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <min> when used with <choices> for type <%s>." %(iPar['name'],xSection,iPar['type']))
            else: #float or (int && noChoice)
                isMin = True
        if ('max' in iPar):
            if (iPar['type'] not in 'integer'):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <max> for type <%s>." %(iPar['name'],xSection,iPar['type']))
            elif ( isChoices and (iPar['type'] in 'integer')):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <max> when used with <choices> for type <%s>." %(iPar['name'],xSection,iPar['type']))
            else: #float or (int && noChoice)
                isMax = True
 
        if (isChoices):
            if ((iPar['type'] in 'integer') or (iPar['type'] in 'string')):
                if (val not in iPar['choices']):
                    logAndExit("Configuration file: Illegal value for <%s> in section [%s]. Value has to be in [%s]." %(iPar['name'],xSection,','.join([str(x) for x in iPar['choices']])))     
        if (isMin):
            if (val < iPar['min']):
                logAndExit(f"Configuration file: The minimum value of <%s> in section [%s] is %d." %(iPar['name'],xSection,iPar['min']))
        if (isMax and (val > iPar['max'])):
            logAndExit(f"Configuration file: The maximum value of <%s> in section [%s] is %d." %(iPar['name'],xSection,iPar['max']))

        setSetting(iPar['name'],val)

    if (not setup):
        for option,isItLegal in optionsInConfig.items():
            if (not isItLegal):
                warnAndLog("Configuration file: Unrecognized option <%s> in section [%s]. This value is going to be ignored." %(option,xSection))

    return


