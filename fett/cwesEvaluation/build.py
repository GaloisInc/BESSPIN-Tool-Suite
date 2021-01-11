"""
Building CWEs Evaluation
"""

import glob, os, re, random
from collections import defaultdict
from pathlib import Path

from fett.base.utils.misc import *
from fett.cwesEvaluation.bufferErrors.generateTests.generateTests import generateTests
from fett.cwesEvaluation.informationLeakage.generateWrappers import generateWrappers
from fett.cwesEvaluation.utils.templateFreeRTOS import templateFreeRTOS
from fett.cwesEvaluation.common import isTestEnabled
from fett.target.build import freeRTOSBuildChecks, buildFreeRTOS, crossCompileUnix, cleanDirectory
from fett.cwesEvaluation.informationLeakage.cweScores import generateCweMap
from fett.cwesEvaluation.bufferErrors.count import bfparams

@decorate.debugWrap
def buildCwesEvaluation():
    # Create build directory
    buildDir = os.path.join(getSetting('workDir'), 'build')
    mkdir(buildDir, addToSettings="buildDir")

    if isEqSetting('osImage', 'FreeRTOS'):
        # create the osImages directory
        osImagesDir = os.path.join(getSetting('workDir'),'osImages')
        mkdir(osImagesDir,addToSettings='osImagesDir')
        # TODO: Might need do do something special for SRI-Cambridge (see
        # prepareOsImage in target/build.py)
        osImageElf = os.path.join(getSetting('osImagesDir'),f"{getSetting('osImage')}.elf")
        setSetting('osImageElf',osImageElf)
        setSetting('osImageExtraElf', None)
        setSetting('osImageAsm',
                   os.path.join(getSetting('osImagesDir'),
                                f"{getSetting('osImage')}.asm"))
        setSetting('sendTarballToTarget', False)

        freeRTOSBuildChecks()

        if (isEqSetting('binarySource','LMCO')):
            cp (os.path.join(getSetting('repoDir'),'fett','cwesEvaluation','utils','lmcoMiscFreeRTOS.c'),
                getSetting('buildDir'))

        configHfile = ftOpenFile (os.path.join(getSetting('buildDir'),'fettUserConfig.h'),'a')
        configHfile.write(f"#define BIN_SOURCE_{getSetting('binarySource').replace('-','_')}\n")
        configHfile.close()
        touch(os.path.join(getSetting('buildDir'), "fettFreeRTOSConfig.h"))

        if (isEnabled('useCustomCompiling') and isEnabledDict('customizedCompiling','useCustomMakefile')):
            cp (getSettingDict('customizedCompiling','pathToCustomMakefile'),
                os.path.join(getSetting('buildDir'), 'Makefile'))

        for vClass in ["PPAC"]:
            if (vClass in getSetting("vulClasses")):
                warnAndLog(f"vulClass <{vClass}> is not supported on FreeRTOS. "
                    f"<{vClass}> will be skipped.")
                getSetting("vulClasses").remove(vClass)

        fillerCfile = os.path.join(getSetting('repoDir'),'fett','cwesEvaluation','utils','fillerMainFreeRTOS.c')

    # Copy tests over
    enabledCwesEvaluations = defaultdict(list)
    isThereAnythingToRun = False
    isThereAReasonToBoot = False
    for vulClass in getSetting('vulClasses'):
        vIsThereAnythingToRun = False
        # Create class dir and build
        vulClassDir = os.path.join(buildDir, vulClass)
        mkdir(vulClassDir)
        sourcesDir = os.path.join(getSetting('repoDir'),'fett','cwesEvaluation',
                                vulClass, 'sources')

        if vulClass == 'bufferErrors':
            vIsThereAnythingToRun = True
            cp (os.path.join(getSetting('repoDir'),'fett','cwesEvaluation',
                                    vulClass,'envFett.mk'), vulClassDir)
            # Generate test sources
            generateTests(vulClassDir)
            if (isEnabledDict(vulClass,'useSelfAssessment')):
                enabledCWEs = set()
                for cFile in glob.glob(os.path.join(vulClassDir,"*.c")):
                    testParams = bfparams(Path(cFile))
                    if ('CWE' in testParams):
                        enabledCWEs.update(set(testParams['CWE']))
                    else:
                        warnAndLog(f"buildCwesEvaluation: Failed to parse the CWE parameters in {cFile}.")
                enabledCwesEvaluations[vulClass] = sorted(
                        [cwe.replace('CWE_','test_') + ".riscv" for cwe in enabledCWEs]
                    )
            else:
                isThereAReasonToBoot = True
                if isEnabledDict('bufferErrors', 'useExtraTests'):
                    # Copy extra tests over, prepending C files with 'test_extra_'
                    extraSources = getSettingDict('bufferErrors', 'extraSources')
                    if extraSources[0] != '/':
                        extraSources = os.path.join(getSetting('repoDir'),
                                                    extraSources)
                    for source in glob.glob(os.path.join(extraSources, '*.c')):
                        cp(source,
                           os.path.join(vulClassDir,
                                        f'test_extra_{os.path.basename(source)}'))
                enabledCwesEvaluations[vulClass] = [os.path.basename(f).replace(".c",".riscv") for f in
                    glob.glob(os.path.join(vulClassDir,"*.c"))]
        elif vulClass == 'informationLeakage':
            cp (os.path.join(getSetting('repoDir'),'fett','cwesEvaluation',
                                    vulClass,'envFett.mk'), vulClassDir)
            # Copy over concrete tests
            copyDir(sourcesDir, vulClassDir, copyContents=True)
            enabledDrivers, enabledBins = generateWrappers()
            vIsThereAnythingToRun = (len(enabledDrivers) > 0)
            if (vIsThereAnythingToRun):
                if (isEnabledDict(vulClass,'useSelfAssessment')):
                    cweMap = generateCweMap()
                    try: 
                        enabledCWEs = set()
                        for driver in enabledDrivers:
                            enabledCWEs.update(set(cweMap[driver]))
                        enabledCwesEvaluations[vulClass] = sorted(
                                [cwe.replace('CWE_','test_') + ".riscv" for cwe in enabledCWEs]
                            )
                    except Exception as exc:
                        logAndExit(f"buildCwesEvaluation: Failed to generate the tests list from the input ini "
                            f"configuration for <informationLeakage> in <selfAssessment> mode.",exc=exc,exitCode=EXIT.Dev_Bug)
                else:
                    isThereAReasonToBoot = True
                    enabledCwesEvaluations[vulClass] = enabledBins
        else:
            if (isEnabledDict(vulClass,'useSelfAssessment')):
                tests = getSettingDict(vulClass,["testsInfo"])
            else: #all C files in sources
                cp (os.path.join(sourcesDir,'envFett.mk'), vulClassDir)
                tests = [os.path.basename(f).split(".c")[0] for f in glob.glob(os.path.join(sourcesDir, "test_*.c"))]
                if (doesSettingExistDict(vulClass,["mapTestsToCwes"])): #this class has special maps
                    for cweTest, testsList in getSettingDict(vulClass,["mapTestsToCwes"]).items():
                        for test in testsList:
                            isAlreadyEnabled = getSettingDict(vulClass,['enabledTests',test], default=False)
                            setSettingDict( vulClass,['enabledTests',test],
                                    (isAlreadyEnabled or isTestEnabled(vulClass,cweTest)) )
            for test in tests:
                # Check if the test should be skipped:
                if (isTestEnabled(vulClass,test)):
                    vIsThereAnythingToRun = True
                    if (not isEnabledDict(vulClass,'useSelfAssessment')): #No need to boot for self-assessment
                        isThereAReasonToBoot = True 
                        cp (os.path.join(sourcesDir, f"{test}.c"), vulClassDir)
                    enabledCwesEvaluations[vulClass].append(f"{test}.riscv")
                else:
                    printAndLog(f"buildCwesEvaluation: Skipping <{vulClass}:{test}>. It is not enabled.",doPrint=False)

        isThereAnythingToRun |= vIsThereAnythingToRun
        if (not vIsThereAnythingToRun):
            continue

        if (not isEqSetting('osImage', 'FreeRTOS')):
            # copy makefile over
            if (isEnabled('useCustomCompiling') and isEnabledDict('customizedCompiling','useCustomMakefile')):
                cp (getSettingDict('customizedCompiling','pathToCustomMakefile'),
                    os.path.join(vulClassDir, 'Makefile'))
            else: # Use default environment
                if (doesSettingExistDict(vulClass, "classSpecificMake") and
                    isEnabledDict(vulClass, "classSpecificMake")):
                    cp(os.path.join(getSetting('repoDir'),
                                    'fett',
                                    'cwesEvaluation',
                                    vulClass,
                                    'Makefile.xcompileDir'),
                       os.path.join(vulClassDir, 'Makefile'))
                else:
                    cp(os.path.join(getSetting('repoDir'),
                                    'fett',
                                    'target',
                                    'utils',
                                    'Makefile.xcompileDir'),
                       os.path.join(vulClassDir, 'Makefile'))
                cp(os.path.join(getSetting('repoDir'),
                                'fett',
                                'target',
                                'utils',
                                'defaultEnvUnix.mk'),
                    vulClassDir)

        #Set the list of enabled tests
        setSetting('enabledCwesEvaluations', enabledCwesEvaluations)

        if (isEnabledDict(vulClass,'useSelfAssessment')):
            continue
        # Write the extra testsParameters.h
        fHeader = ftOpenFile(os.path.join(vulClassDir, "testsParameters.h"), 'w')
        for xSetting, xVal in getSetting(vulClass).items():
            if (xSetting.startswith('test_')):
                settingName = xSetting.split('test_')[-1]
                fHeader.write(f"#define {settingName} {xVal}\n")
        if (vulClass == "resourceManagement"):
            if (isEnabledDict(vulClass,"useSeed")):
                seed = getSettingDict(vulClass,"seed")
                printAndLog(f"{vulClass}: Using the custom seed <{seed}>.")
            else:
                seed = random.randrange(pow(2,32)) #This is the maximum value in configData.json (-1 of course)
                printAndLog(f"{vulClass}: Using the seed <{seed}>.")
            fHeader.write(f"#define RM_SEED {seed}\n")
        fHeader.close()

        if isEqSetting('osImage', 'FreeRTOS'):
            templateFreeRTOS(vulClassDir)
        elif getSetting('osImage') in ['debian', 'FreeBSD']:
            crossCompileUnix(vulClassDir,extraString=f'{vulClass} tests')
        else:
            logAndExit("<buildCwesEvaluation> is not implemented for "
                       f"<{getSetting('osImage')}>.",
                       exitCode=EXIT.Implementation)

    if getSetting('osImage') in ['debian', 'FreeBSD']:
        setSetting('isThereAReasonToBoot',isThereAReasonToBoot) #This is set per class in FreeRTOS
        buildTarball()
    return isThereAnythingToRun

@decorate.debugWrap
@decorate.timeWrap
def buildTarball():
    fileList = [(os.path.basename(f), f) for f in
                glob.glob(os.path.join(getSetting('buildDir'),
                                       "*",
                                       "*.riscv"))]

    fileList += [(os.path.basename(f), f) for f in
                 glob.glob(os.path.join(getSetting("buildDir"), "*.riscv"))]

    if (len(fileList)>0):
        logging.debug(f"buildTarball: The tarball will contain the following: {fileList}.")
        tar(os.path.join(getSetting("buildDir"), getSetting('tarballName')),
            fileList)
        setSetting('sendTarballToTarget', True)
    else:
        logging.debug("buildTarball: There are no files to send to target. No need to create a tarball.")
        setSetting('sendTarballToTarget', False)

@decorate.debugWrap
@decorate.timeWrap
def buildFreeRTOSTest(test, vulClass, part, testLogFile):
    if (part==0):
        logging.debug(f"buildFreeRTOSTest: <{test}> is called with [part=0]. Skipping the build.")
        return

    buildDir = getSetting('buildDir')
    
    # copy the test files
    vTestsDir = os.path.join(buildDir, vulClass)
    testFiles = [test, f'main_{test}', 'testsParameters.h', 'envFett.mk']

    for testFile in testFiles:
        cp (os.path.join(vTestsDir,testFile), buildDir)

    fPars = ftOpenFile(os.path.join(buildDir,'testsParameters.h'),'a')
    fPars.write(f"\n#define TESTGEN_TEST_PART {part}\n")
    fPars.close()

    # Build
    if ((vulClass == "informationLeakage") 
            and (test.split(".c")[0] not in getSettingDict("informationLeakage","nonstandardTests"))):
        testInfo = os.path.splitext(os.path.basename(test))[0].split("_")[1:]
        variantNames = (f"informationLeakage/tests/{testInfo[0]}.c "
                        f"informationLeakage/stores/{testInfo[1]}.c "
                        f"informationLeakage/interpreters/{testInfo[2]}.c")
        extraEnvVars = [f"VARIANT_NAMES={variantNames}"]
    else:
        extraEnvVars = []
    buildFreeRTOS(doPrint=False, extraEnvVars=extraEnvVars)

    #remove the current test files
    for testFile in testFiles:
        os.remove(os.path.join(buildDir,testFile))
    #remove the object files
    cleanDirectory (buildDir,endsWith='.o')
