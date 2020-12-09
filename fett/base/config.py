#! /usr/bin/env python3
"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file parses the input configuration ini file, checks its legality, and stores all the settings.
json details are in: ./utils/configData.json
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

import configparser, json, os, re
import base64
from fett.base.utils.misc import *
from importlib.machinery import SourceFileLoader
from fett.cwesEvaluation.scoreTests import SCORES

COMMON_SECTIONS = ['functionality', 'common', 'applications', 'build']
TARGET_SECTION = 'target'
CWES_SECTION = 'evaluateSecurityTests'
CYBERPHYS_SECTION = 'cyberPhys'

def loadJsonFile (jsonFile):
    try:
        fJson = open(jsonFile,'r')
        jsonData = json.load(fJson)
        fJson.close()
    except Exception as exc:
        logAndExit(f"Failed to load json file <{jsonFile}>.",exc=exc,exitCode=EXIT.Files_and_paths)
    return jsonData

def loadIniFile (iniFile):
    xConfig = configparser.ConfigParser()
    try:
        fConfig = open(iniFile,'r')
        xConfig.read_file(fConfig)
        fConfig.close()
    except Exception as exc:
        logAndExit(f"Failed to read configuration file <{iniFile}>.",exc=exc,exitCode=EXIT.Files_and_paths)
    return xConfig

@decorate.debugWrap
def loadConfiguration(configFile):
    #loading dev setup environment
    setupEnvData = loadJsonFile(getSetting('setupEnvFile'))
    loadConfigSection(None,None,setupEnvData,'setupEnv',setup=True)

    #loading the configuration file
    xConfig = loadIniFile(configFile)

    #loading the configuration parameters data
    configDataFile = getSetting('jsonDataFile')
    configData = loadJsonFile(configDataFile)

    # Here we should read the options and such
    for xSection in COMMON_SECTIONS:
        loadConfigSection (xConfig,xSection,configData,xSection)

    """
    *** How to handle going from a single target to many targets for cyberPhys? ***
    - In settings, the target settings are either loaded, or they are loaded inside [target${i}].
      It is done this way to protect both the one-target functionality and the many-targets
      functionality.
    - If the developer uses a method that was not adapted to use many-targets, it will give an 
      error in fetching the settings. This is better than just going ahead with the wrong setting 
      and let you chase why the tool is not doing what you are trying to instruct it to do.
    """
    if isEqSetting('mode','cyberPhys'):
        loadConfigSection(xConfig,CYBERPHYS_SECTION,configData,CYBERPHYS_SECTION)
        loadCyberPhysConfiguration(configData)
    else: #load the one-target
        loadConfigSection(xConfig,TARGET_SECTION,configData,TARGET_SECTION)
        setExtraTargetSettings()

    # Load evaluateSecurityTests related sections
    if isEqSetting("mode", "evaluateSecurityTests"):
        loadSecurityEvaluationConfiguration(xConfig,configData)

    if isEnabled('useCustomCredentials'):
        # Check username is legal
        userName = getSetting("userName")
        if re.fullmatch("[a-zA-Z0-9]{1,14}", userName) is None:
            logAndExit(f"userName \"{userName}\" does not satisfy the username "
                       "requirements.  Must be 1-14 characters long and may "
                       "consist only of alphanumeric ASCII characters.")

        # Check password hash is legal
        # Should look like: $6$<salt>$<SHA-512 hash>
        # The "6" at the beginning identifies the hash as SHA-512, which is what
        # our debian and FreeBSD installs expect
        # <salt> may be up to 16 characters [a-zA-Z0-9./]
        # <SHA-512 hash> must be exactly 86 characters in [a-zA-Z0-9./]
        userPasswordHash = getSetting("userPasswordHash")
        if re.fullmatch("\\$6\\$[a-zA-Z0-9./]{0,16}\\$[a-zA-Z0-9./]{86}", userPasswordHash) is None:
            logAndExit(f"userPasswordHash \"{userPasswordHash}\" is not a legal "
                       "password hash.  Must be a SHA-512 encrypted hash produced "
                       "by crypt(3).")

    printAndLog('Configuration loaded successfully.')
    dumpSettings()
    return

@decorate.debugWrap
def setExtraTargetSettings(targetId=None):
    # Get the XLEN and processor flavor
    procMatch = re.match(r"^(?P<procFlavor>chisel|bluespec)_p(?P<procLevel>[1-3])$",getSetting('processor', targetId=targetId))
    if (procMatch):
        setSetting('procFlavor', procMatch.group('procFlavor'), targetId=targetId)
        setSetting('procLevel', f"p{procMatch.group('procLevel')}", targetId=targetId)
        if (procMatch.group('procLevel') == '1'):
            setSetting('xlen', 32, targetId=targetId)
        else: # 2-3
            setSetting('xlen', 64, targetId=targetId)
    else:
        logAndExit(f"Failed to determine the processor flavor and xlen for <{getSetting('processor',targetId=targetId)}>.",exitCode=EXIT.Dev_Bug)

    # Create an isUnix setting
    setSetting('isUnix',getSetting('osImage',targetId=targetId) in ['debian', 'FreeBSD', 'busybox'], targetId=targetId)


@decorate.debugWrap
def loadConfigSection (xConfig,configSection,jsonData,dataSection,setup=False,
                        addSectionToConfigDict=None,setSettingsToSectDict=False):
    if (setup):
        fileName = "SetupEnv file"
    else:
        fileName = "Configuration file"

    if (not setup):
        try:
            assert xConfig.has_section(configSection), f"has_section('{configSection}')"
        except Exception as exc:
            logAndExit(f"Section <{configSection}> not found in configuration file.",exc=exc,exitCode=EXIT.Configuration)
        optionsInConfig = dict.fromkeys(xConfig.options(configSection),False) #to see if some unwanted parameters in config file
    
    try:
        jsonPars = jsonData[dataSection]
    except Exception as exc:
        logAndExit(f"Section <{dataSection}> not found in json configuration info file.",exc=exc,exitCode=EXIT.Configuration)

    if (addSectionToConfigDict):
        try:
            jsonPars += jsonData[addSectionToConfigDict]
        except Exception as exc:
            logAndExit(f"Section <{addSectionToConfigDict}> not found in json configuration info file.",exc=exc,exitCode=EXIT.Dev_Bug)

    for iPar in jsonPars:
        if (('name' not in iPar) or ('type' not in iPar)):
            logAndExit("While reading json configuration info file. <%s> is missing a <name> or <type> in section [%s]." %(iPar['name'],dataSection),exitCode=EXIT.Configuration)
        #checking the value types + fetching the values--------------
        if (setup):
            if ('val' not in iPar):
                logAndExit(f"While reading json setupEnv file. <{iPar['name']}> is missing <val>.",exitCode=EXIT.Configuration)
        else:
            try:
                assert xConfig.has_option(configSection,iPar['name']), f"has_option('{iPar['name']}')"
            except Exception as exc:
                logAndExit(f"{fileName}: <{iPar['name']}> not found in section [{configSection}].",exc=exc,exitCode=EXIT.Configuration)
            optionsInConfig[iPar['name'].lower()] = True #Be careful! configparser options are always case insensitive and are all lowercase
        
        if (iPar['type'] in 'integer'): #works for int or integer
            try:
                if (setup):
                    val = int(iPar['val'])
                else:
                    val = xConfig.getint(configSection,iPar['name'])
            except Exception as exc:
                logAndExit(f"{fileName}: <{iPar['name']}> has to be integer in section [{configSection}].",exc=exc,exitCode=EXIT.Configuration)
        elif (iPar['type'] in 'boolean'): #works for bool or boolean
            try:
                if (setup):
                    val = bool(int(iPar['val']))
                else:
                    val = xConfig.getboolean(configSection,iPar['name'])
            except Exception as exc:
                logAndExit(f"{fileName}: <{iPar['name']}> has to be boolean in section [{configSection}].",exc=exc,exitCode=EXIT.Configuration)
        elif ( iPar['type'] in ['str', 'string', 'stringsList', 'filePath', 'dirPath', 'ipAddress', 
                                'dict', 'macAddress', 'hex', 'hexList', 'hexPairsList']): 
            if (setup):
                val = iPar['val']
            else:
                val = xConfig.get(configSection,iPar['name'])
            if (len(val)==0):
                warnAndLog(f"{fileName}: The setting <{iPar['name']}> in section [{configSection}] is empty!")
            if ('#' in val):
                logAndExit(f"{fileName}: Illegal character in <{iPar['name']}> in section [{configSection}]. Is there a comment next to the value?",exitCode=EXIT.Configuration)
            if (iPar['type'] in ['filePath','dirPath']):
                doCheckPath = True
                if (setup):
                    val = os.path.join(getSetting('repoDir'),val)
                if (not setup and ('condition' in iPar)): #skip checking the path if the setting is disabled
                    if (xConfig.has_option(configSection,iPar['condition'])):
                        try:
                            doCheckPath = xConfig.getboolean(configSection,iPar['condition'])
                        except Exception as exc:
                            logAndExit("Configuration file: <%s> has to be boolean in section [%s]." %(iPar['condition'],configSection),exc=exc,exitCode=EXIT.Configuration)
                    else:
                        logAndExit(f"Configuration file: The condition <{iPar['condition']}> is not found in section [{configSection}].",exitCode=EXIT.Configuration)
                elif (setup and ('condition' in iPar)):
                    logAndExit (f"The <condition> option is not yet implemented for the setupEnv json.",exitCode=EXIT.Configuration)
                if (doCheckPath):
                    if ((iPar['type'] == 'filePath') and (not os.path.isfile(val))):
                        logAndExit(f"{fileName}: <{iPar['name']}> has to be a valid file path in section [{configSection}].",exitCode=EXIT.Configuration)
                    if ((iPar['type'] == 'dirPath') and (not os.path.isdir(val))):
                        logAndExit(f"{fileName}: <{iPar['name']}> has to be a valid directory path in section [{configSection}].",exitCode=EXIT.Configuration)
            elif (iPar['type'] == 'ipAddress'):
                ipMatch = re.match(r"(\d{1,3}\.){3}\d{1,3}$",val)
                if (ipMatch is None):
                    logAndExit(f"{fileName}: <{iPar['name']}> has to be a valid IP address in section [{configSection}].",exitCode=EXIT.Configuration)
            elif (iPar['type'] == 'macAddress'):
                macAddressMatch = re.match(r"([0-9a-fA-F]{2}\:){5}[0-9a-fA-F]{2}$",val)
                if (macAddressMatch is None):
                    logAndExit(f"{fileName}: <{iPar['name']}> has to be a valid MAC address in section [{configSection}].",exitCode=EXIT.Configuration)
            elif (iPar['type'] == 'hex'):
                try:
                    val = int(val,16)
                except Exception as exc:
                    logAndExit(f"ValueError in reading configuration file. <{iPar['name']}> has to be hex in"
                            f" section [{configSection}].",exc=exc,exitCode=EXIT.Configuration)
            elif ('List' in iPar['type']):
                if ((val[0] != '[') or (val[-1] != ']')):
                    logAndExit("ValueError in reading configuration file. <{iPar['name']}> has to be of type "
                               f"{iPar['type']} in section [{configSection}]. A {iPar['type']} has to have contents between brackets.",
                               exitCode = EXIT.Configuration)
                if (len(val[1:-1]) == 0):
                    vals = []
                else:
                    # transform val into a python list of strings
                    vals = [x.strip() for x in val[1:-1].split(',')]
                if (iPar['type'] == 'hexPairsList'): #check that they are hex
                    for val in vals:
                        items = val.split(':')
                        if (len(items)!=2):
                            logAndExit(f"ValueError in reading configuration file. <{iPar['name']}> has to be a colon-separated hex-pair"
                                    f" in section [{configSection}].",exitCode=EXIT.Configuration)
                        for item in items:
                            try:
                                xHex = int(item,16)
                            except Exception as exc:
                                logAndExit(f"ValueError in reading configuration file. The value <{item}> in the pair <{val}> of the"
                                        f" parameter <{iPar['name']}> is not hex in section [{configSection}].",exc=exc,exitCode=EXIT.Configuration)
                elif (iPar['type'] == 'hexList'): #check that they are hex
                    if (('wildValue' in iPar) and (iPar['wildValue'] in vals)):
                        vals = ['ALL']
                    else:
                        exceptionValue = None
                        if ("exception" in iPar): #the value in this option is not allowed
                            if (xConfig.has_option(configSection,iPar['exception'])):
                                try:
                                    exceptionValue = int(xConfig.get(configSection,iPar['exception']),16)
                                except Exception as exc:
                                    logAndExit(f"ValueError in reading configuration file. <{iPar['exception']}> has to be hex in "
                                            f"section [{configSection}].",exc=exc,exitCode=EXIT.Configuration)
                        for iVal in range(len(vals)):
                            try:
                                vals[iVal] = int(vals[iVal],16)
                            except Exception as exc:
                                logAndExit(f"ValueError in reading configuration file. The value <{vals[iVal]}> in <{iPar['name']}> is"
                                            f" not hex in section [{configSection}].",exc=exc,exitCode=EXIT.Configuration)
                            if ((exceptionValue is not None) and (vals[iVal] == exceptionValue)):
                                logAndExit(f"ValueError in reading configuration file. The value <{vals[iVal]}> in <{iPar['name']}> cannot "
                                            f"equal the exception value <{iPar['exception']}> in section [{configSection}].",exitCode=EXIT.Configuration)
        else:
            logAndExit(f"Json info file: Unknown type <{iPar['type']}> for <{iPar['name']}> in section [{dataSection}].",exitCode=EXIT.Configuration)

        #checking the values choices + limits
        isChoices= False
        isMin = False
        isMax = False
        isSize = False
        if ('choices' in iPar):
            if ( (iPar['type'] not in 'string') and
                 (iPar['type'] not in 'integer') and
                 (iPar['type'] not in 'stringsList') ):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <choices> for type <%s>." %(iPar['name'],dataSection,iPar['type']))
            else: #int, str, stringsList
                isChoices = True
        if ('min' in iPar):
            if ( (iPar['type'] not in 'integer') and ('hex' not in iPar['type']) ):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <min> for type <%s>." %(iPar['name'],dataSection,iPar['type']))
            elif ( isChoices and (iPar['type'] in 'integer')):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <min> when used with <choices> for type <%s>." %(iPar['name'],dataSection,iPar['type']))
            else: #float or (int && noChoice)
                isMin = True
        if ('max' in iPar):
            if (iPar['type'] not in 'integer'):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <max> for type <%s>." %(iPar['name'],dataSection,iPar['type']))
            elif ( isChoices and (iPar['type'] in 'integer')):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <max> when used with <choices> for type <%s>." %(iPar['name'],dataSection,iPar['type']))
            else: #float or (int && noChoice)
                isMax = True
        if ('size' in iPar):
            if (iPar['type'] == 'hexPairsList'):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <size> for type <%s>. Not implemented." %(iPar['name'],dataSection,iPar['type']))
            elif ('hex' not in iPar['type']):
                warnAndLog("Json configuration info file: For <%s> in section [%s]: Ignoring <size> for type <%s>." %(iPar['name'],dataSection,iPar['type']))
            else:
                isSize = True
 
        if (isChoices):
            if ((iPar['type'] in 'integer') or (iPar['type'] in 'string')):
                if (val not in iPar['choices']):
                    logAndExit("Configuration file: Illegal value for <%s> in section [%s]. Value has to be in [%s]." %(iPar['name'],configSection,','.join([str(x) for x in iPar['choices']])))     
            elif (iPar['type'] == 'stringsList'):
                for val in vals:
                    if (val not in iPar['choices']):
                        # Leaving the "str(x) for x in case we need to
                        # implement a list of integers"
                        logAndExit("ValueError in reading configuration file. "
                                   "Illegal value for <%s> in section [%s]. "
                                   "Value has to be in [%s]." %
                                   (iPar['name'],
                                    configSection,
                                    ','.join([str(x) for x in iPar['choices']])),
                                   exitCode = EXIT.Configuration)
        if (isMin):
            if ('List' in iPar['type']):
                if (vals != ['ALL']):
                    for val in vals:
                        if (val < iPar['min']):
                            logAndExit("Configuration file: The minimum value of <%s> in section [%s] is %d." %(iPar['name'],configSection,iPar['min']))
            elif (val < iPar['min']):
                logAndExit("Configuration file: The minimum value of <%s> in section [%s] is %d." %(iPar['name'],configSection,iPar['min']))
        if (isMax and (val > iPar['max'])):
            logAndExit("Configuration file: The maximum value of <%s> in section [%s] is %d." %(iPar['name'],configSection,iPar['max']))
        if (isSize):
            if ('List' in iPar['type']):
                if (vals != ['ALL']):
                    for val in vals:
                        if (val > int('0x' + 'F'*iPar['size'] ,16)):
                            logAndExit("Configuration file: The maximum size of the elements of <%s> in section [%s] is %d nibbles." %(iPar['name'],configSection,iPar['size']))
            elif (val > int('0x' + 'F'*iPar['size'] ,16)):
                logAndExit("Configuration file: The maximum size of <%s> in section [%s] is %d nibbles." %(iPar['name'],configSection,iPar['size']))

        settingVal = vals if ('List' in iPar['type']) else val
        if (setSettingsToSectDict):
            setSettingDict(setSettingsToSectDict,iPar['name'],settingVal)
        else:
            setSetting(iPar['name'],settingVal)

    if (not setup):
        for option,isItLegal in optionsInConfig.items():
            if (not isItLegal):
                warnAndLog("Configuration file: Unrecognized option <%s> in section [%s]. This value is going to be ignored." %(option,configSection))

    return

@decorate.debugWrap
def genProdConfig(configFileSerialized, configFile):
    """
    This generates "production.ini":
    - Loads the template from config.ini.
    - Overwrites the template using the production template.
    - Overwrites whatever is provided from the serialized input.
    - Generate the configFile to be used by the tool
    """

    #loading the template configuration file (the repo's default)
    templateConfigPath = os.path.join(getSetting('repoDir'),'config.ini')
    xConfig = loadIniFile(templateConfigPath)

    # loading the production template
    prodTemplatePath = os.path.join(getSetting('repoDir'),'fett','base','utils','productionTemplate.json')
    prodSettings = loadJsonFile(prodTemplatePath)

    # deserialize the input
    try:
        inputSettings = json.loads(configFileSerialized)
    except Exception as exc:
        logAndExit(f"Failed to deserialize <{configFileSerialized}>. Please check the syntax.",exc=exc,exitCode=EXIT.Configuration)

    # Overwrites the settings
    prodSettings.update(inputSettings)
    
    # Overwrite the options based on the production template + input settings
    for xSetting, xValue in prodSettings.items():
        wasSet = False
        for xSection in xConfig:
            if (xSetting in xConfig[xSection]):
              if(xSetting == "userPasswordHash"):
                try:
                    xValue = base64.b64decode(xValue).decode("utf-8")
                except Exception as exc:
                    logAndExit(f"Failed to decode the <userPasswordHash>.",exc=exc,exitCode=EXIT.Configuration)
              xConfig.set(xSection,xSetting,str(xValue))
              wasSet = True
              break
        if (not wasSet):
            logAndExit(f"Failed to find the production setting <{xSetting}> in <{templateConfigPath}>.",exitCode=EXIT.Configuration)

    # Create the config file
    try:
        fConfig = open(configFile,'w')
        xConfig.write(fConfig)
        fConfig.close()
    except Exception as exc:
        logAndExit(f"Failed to write configuration file <{configFile}>.",exc=exc,exitCode=Files_and_paths)
    
@decorate.debugWrap
def loadSecurityEvaluationConfiguration (xConfig,configData):
    #load main global configs
    loadConfigSection(xConfig, CWES_SECTION, configData, CWES_SECTION)

    #The location of all the vulClass.ini files
    if (isEnabled('useCustomCWEsConfigsPath')):
        configCWEsParentPath = getSetting('pathToCustomCWEsConfigs')
    else: #use default
        configCWEsParentPath = os.path.join(getSetting('repoDir'),'configSecurityTests')

    # load vulClass configs
    for vulClass in getSetting('vulClasses'): #load settings per vulClass
        vulClassDict = dict()
        setSetting(vulClass,vulClassDict)
        loadConfigSection(xConfig, vulClass, configData, vulClass, 
                addSectionToConfigDict='commonVulClassesParameters', setSettingsToSectDict=vulClass)

        configCWEsPath = os.path.join(configCWEsParentPath,f'{vulClass}.ini')

        if (vulClass in ['bufferErrors']):
            setSettingDict(vulClass,'runAllTests',True)
            printAndLog(f"loadSecurityEvaluationConfiguration: Always enabling <runAllTests> for <{vulClass}>",doPrint=False)
        elif (isEnabled('useCustomCWEsConfigsPath') and isEnabledDict(vulClass,'runAllTests')):
            warnAndLog(f"{vulClass}: <runAllTests> is enabled; The <test_*> settings in <{configCWEsPath}>"
                f"will be ignored.") 
            # The ignoring happens in fett/cwesEvaluation/common.py:isTestEnabled() which checks
            # the `runAllTests` setting _before_ proceeding and checking the `test_*` setting.

        # Load selected tests + custom scores
        sectionName = 'configCWEs'
        configCWEs = loadIniFile(configCWEsPath)
        try:
            assert configCWEs.has_section(sectionName), f"has_section('{sectionName}')"
        except Exception as exc:
            logAndExit(f"Section <{sectionName}> not found in <{configCWEsPath}>.",exc=exc,exitCode=EXIT.Configuration)

        dictConfigCWEs = dict() 
        for xTest in configCWEs.options(sectionName):
            try:
                dictConfigCWEs[xTest] = configCWEs.getboolean(sectionName,xTest)
            except Exception as exc:
                logAndExit(f"The value of <{xTest}> should be boolean in <{configCWEsPath}>.",exc=exc,exitCode=EXIT.Configuration)

            setSettingDict(vulClass,'configCWEs',dictConfigCWEs)

        # Load custom dev options (setupEnv.json)
        setupEnvData = loadJsonFile(os.path.join(getSetting('repoDir'),'fett','cwesEvaluation',vulClass,'setupEnv.json'))
        loadConfigSection(None,None,setupEnvData,vulClass,setup=True,setSettingsToSectDict=vulClass)

    # Load custom scoring options if enabled
    if (isEnabled('useCustomScoring')):
        customizedScoringDict = dict()
        setSetting('customizedScoring',customizedScoringDict)
        loadConfigSection(xConfig, 'customizedScoring', configData, 'customizedScoring', 
                setSettingsToSectDict='customizedScoring')

        # Check that the custom function is legit
        if (isEnabledDict('customizedScoring','useCustomFunction')):
            if (not checkCustomScorerFunction()):
                logAndExit(f"loadSecurityEvaluationConfiguration: <{getSettingDict('customizedScoring','pathToCustomFunction')}> has to be a valid scoring script.",exitCode=EXIT.Configuration)

    # Load custom compiling options if enabled
    if (isEnabled('useCustomCompiling')):
        customizedCompilingDict = dict()
        setSetting('customizedCompiling',customizedCompilingDict)
        loadConfigSection(xConfig, 'customizedCompiling', configData, 'customizedCompiling', 
                setSettingsToSectDict='customizedCompiling')

@decorate.debugWrap
def checkCustomScorerFunction():
    """
    if both of useCustomScoring and useCustomFunction are enabled, check that the function is working
    """
    customCheckOut = os.path.join(getSetting('workDir'),'customScorerFunctionCheck.out')
    customFuncPath = getSettingDict('customizedScoring','pathToCustomFunction')
    try:
        with redirectPrintToFile(customCheckOut): #disable print
            moduleUnderTest = SourceFileLoader("customScorer", customFuncPath).load_module()
    except Exception as exc:
        errorAndLog(f"Failed to load {customFuncPath} using SourceFileLoader.",exc=exc)
        return False  

    testLines = []
    testLines.append(["One line no end of line"])
    testLines.append([]) #empty list
    testLines.append ([f"Line #{i}" for i in range(25)])
    testLines.append ([f"Line #{i}\r" for i in range(25)])
    for test in testLines:
        try:
            with redirectPrintToFile(customCheckOut): #disable print
                ret = moduleUnderTest.main(test,SCORES)
        except Exception as exc:
            errorAndLog (f"Failed to test main in <{customFuncPath}>.",exc=exc)
            return False
        if (('__class__' not in dir(ret)) or (ret.__class__ != SCORES)):
            errorAndLog(f"Wrong return type in main in <{customFuncPath}>.")
            return False
    return True

@decorate.debugWrap
def loadCyberPhysConfiguration (configData):
    #load the cyberPhys Config file
    if (isEnabled('useCustomCyberPhysConfig')):
        cyberPhysConfigFile = getSetting('pathToCustomCyberPhysConfig')
    else:
        cyberPhysConfigFile = getSetting('cyberPhysDefaultConfigFile')
    xConfig = loadIniFile(cyberPhysConfigFile)

    for iTarget in range(1,getSetting('nTargets')+1):
        iTargetDict = dict()
        setSetting(iTarget,iTargetDict)
        loadConfigSection(xConfig, f"target{iTarget}", configData, TARGET_SECTION, 
                setSettingsToSectDict=iTarget)
        setExtraTargetSettings(targetId=iTarget)

