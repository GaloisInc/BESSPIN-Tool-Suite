"""
Building CWEs Evaluation
"""

import glob, os, re, random
from collections import defaultdict
from pathlib import Path

from besspin.base.utils.misc import *
from besspin.cwesEvaluation.bufferErrors.generateTests.generateTests import generateTests
from besspin.cwesEvaluation.informationLeakage.generateWrappers import generateWrappers
from besspin.cwesEvaluation.utils.templateFreeRTOS import templateFreeRTOS
from besspin.cwesEvaluation.common import isTestEnabled
from besspin.target.build import freeRTOSBuildChecks, buildFreeRTOS, crossCompileUnix, cleanDirectory
from besspin.cwesEvaluation.informationLeakage.cweScores import generateCweMap
from besspin.cwesEvaluation.bufferErrors.count import bfparams

@decorate.debugWrap
def buildCwesEvaluation():
    """
    Prepares the tests for CWEs evaluation.  Specifically, this function:

        - On Unix, copies cross compiles enabled C tests if needed.
        - On FreeRTOS, copies and generates supporting C test files without
          cross compiling.
        - Generates tests when needed.

    SIDE-EFFECTS:
    -------------
        - Copies enabled test C and build files to <${workDir}/build>.
        - If information leakage tests are enabled and not running in
          self-assessment mode, this function generates the information leakage
          test wrappers.
        - If buffer errors tests are enabled and not running in self-assessment
          mode, this function generates buffer errors tests.
        - Generates <testsParameters.h> header file for each enabled
          vulnerability class.
        - On Unix:
            - Cross compiles enabled test files for which self assessment is
              disabled.
            - Cross compiles multitasking utility if
              ${runUnixMultitaskingTests} is enabled and if any tests were
              cross compiled.
        - On FreeRTOS:
            - Generates ${buildDir}/besspinUserConfig.h header file.
            - Generates <main> wrappers for the tests.
            - Sets ${osImageElf}, ${osImageExtraElf}, and ${osImageAsm}
              to point to the corresponding FreeRTOS files.

    RETURNS:
    --------
        Boolean.  Whether there are any tests to run.
    """

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

        freeRTOSBuildChecks(freertosFork="classic")

        if (isEqSetting('binarySource','LMCO')):
            cp (os.path.join(getSetting('repoDir'),'besspin','cwesEvaluation','utils','lmcoMiscFreeRTOS.c'),
                getSetting('buildDir'))

        configHfile = ftOpenFile (os.path.join(getSetting('buildDir'),'besspinUserConfig.h'),'a')
        configHfile.write(f"#define BIN_SOURCE_{getSetting('binarySource').replace('-','_')}\n")
        configHfile.close()
        touch(os.path.join(getSetting('buildDir'), "besspinFreeRTOSConfig.h"))

        if (isEnabled('useCustomCompiling') and isEnabledDict('customizedCompiling','useCustomMakefile')):
            cp (getSettingDict('customizedCompiling','pathToCustomMakefile'),
                os.path.join(getSetting('buildDir'), 'Makefile'))

        for vClass in ["PPAC"]:
            if (vClass in getSetting("vulClasses")):
                warnAndLog(f"vulClass <{vClass}> is not supported on FreeRTOS. "
                    f"<{vClass}> will be skipped.")
                getSetting("vulClasses").remove(vClass)

        fillerCfile = os.path.join(getSetting('repoDir'),'besspin','cwesEvaluation','utils','fillerMainFreeRTOS.c')

    # Copy tests over
    enabledCwesEvaluations = defaultdict(list)
    isThereAnythingToRun = False
    isThereAReasonToBoot = False
    for vulClass in getSetting('vulClasses'):
        vIsThereAnythingToRun = False
        # Create class dir and build
        vulClassDir = os.path.join(buildDir, vulClass)
        mkdir(vulClassDir)
        sourcesDir = os.path.join(getSetting('repoDir'),'besspin','cwesEvaluation',
                                vulClass, 'sources')

        if vulClass == 'bufferErrors':
            vIsThereAnythingToRun = True
            cp (os.path.join(getSetting('repoDir'),'besspin','cwesEvaluation',
                                    vulClass,'envBesspin.mk'), vulClassDir)
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
            cp (os.path.join(getSetting('repoDir'),'besspin','cwesEvaluation',
                                    vulClass,'envBesspin.mk'), vulClassDir)
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
            if ((vulClass=="PPAC") or isEnabledDict(vulClass,'useSelfAssessment')):
                tests = getSettingDict(vulClass,["testsInfo"])
            else: #all C files in sources
                cp (os.path.join(sourcesDir,'envBesspin.mk'), vulClassDir)
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
                        if ((vulClass != "PPAC") or ("hasCFile" in tests[test])):
                            cp (os.path.join(sourcesDir, f"{test}.c"), vulClassDir)
                    enabledCwesEvaluations[vulClass].append(f"{test}.riscv")
                else:
                    printAndLog(f"buildCwesEvaluation: Skipping <{vulClass}:{test}>. It is not enabled.",doPrint=False)

        isThereAnythingToRun |= vIsThereAnythingToRun
        if (not vIsThereAnythingToRun):
            continue

        if (not isEqSetting('osImage', 'FreeRTOS')):
            # copy build files over
            copyUnixBuildFiles(vulClassDir, vulClass, True)
            if vulClass == "injection":
                # Copy unix injection helpers over
                cp(sourcesDir, vulClassDir, "inj_unix_helpers.*")


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
        vulClassesSeeds = {"resourceManagement":"RM", "informationLeakage":"IEX"}
        if (vulClass in vulClassesSeeds):
            if (isEnabledDict(vulClass,"useSeed")):
                seed = getSettingDict(vulClass,"seed")
                printAndLog(f"{vulClass}: Using the custom seed <{seed}>.")
            else:
                seed = random.randrange(pow(2,32)) #This is the maximum value in configData.json (-1 of course)
                printAndLog(f"{vulClass}: Using the seed <{seed}>.")
            fHeader.write(f"#define {vulClassesSeeds[vulClass]}_SEED {seed}\n")
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

        if isEnabled("runUnixMultitaskingTests") and isThereAReasonToBoot:
            # Build multitasking utility
            multitaskingDir = os.path.join(buildDir, 'multitasking')
            mkdir(multitaskingDir)
            cp(os.path.join(getSetting('repoDir'),
                            'besspin',
                            'cwesEvaluation',
                            'multitasking',
                            'sources'),
               multitaskingDir,
               '*')
            copyUnixBuildFiles(multitaskingDir, None, False)
            crossCompileUnix(multitaskingDir,
                             extraString="multitasking utility",
                             overrideBareMetal=True)

        buildTarball()
    return isThereAnythingToRun

@decorate.debugWrap
def copyUnixBuildFiles(dest, vulClass, checkClassSpecificMake):
    """
    Copy Unix build files (Makefile, defaultEnvUnix.mk, and unbufferStdout.h)
    to a build directory.

    ARGUMENTS:
    ----------
    dest : String
        Directory to copy build files into.

    vulClass : Optional String
        Vulnerability class being built.  May be <None> iff
        <checkClassSpecificMake> is <False>.

    checkClassSpecificMake : Boolean
        If True, check the setting ${vulClass}[<classSpecificMake>] to
        determine whether the vulnerability class has a special Makefile.  If
        False, ignore this setting and use the default Makefile.

    SIDE-EFFECTS:
    -------------
        - If using custom compiling, copies
          <${customizedCompiling}[${pathToCustomMakefile}]> to
          <dest>.  Otherwise, copies Makefile for <vulClass>, as
          well as <${repoDir}/besspin/target/utils/defaultEnvUnix.mk> and
          <${repoDir}/besspin/cwesEvaluation/utils/unbufferStdout.h> to <dest>.
    """
    # copy makefile over
    if (isEnabled('useCustomCompiling') and
        isEnabledDict('customizedCompiling','useCustomMakefile')):
        cp (getSettingDict('customizedCompiling','pathToCustomMakefile'),
            os.path.join(dest, 'Makefile'))
    else: # Use default environment
        if (checkClassSpecificMake and
            doesSettingExistDict(vulClass, "classSpecificMake") and
            isEnabledDict(vulClass, "classSpecificMake")):
            cp(os.path.join(getSetting('repoDir'),
                            'besspin',
                            'cwesEvaluation',
                            vulClass,
                            'Makefile.xcompileDir'),
               os.path.join(dest, 'Makefile'))
        else:
            cp(os.path.join(getSetting('repoDir'),
                            'besspin',
                            'target',
                            'utils',
                            'Makefile.xcompileDir'),
               os.path.join(dest, 'Makefile'))
        cp(os.path.join(getSetting('repoDir'),
                        'besspin',
                        'target',
                        'utils',
                        'defaultEnvUnix.mk'),
            dest)
        cp(os.path.join(getSetting('repoDir'),
                        'besspin',
                        'cwesEvaluation',
                        'utils',
                        'unbufferStdout.h'),
            dest)

@decorate.debugWrap
@decorate.timeWrap
def buildTarball():
    """
    Build a tarball containing the compiled CWE tests.

    SIDE-EFFECTS:
    -------------
        - If there are no compiled binaries:
            - Sets ${sendTarballToTarget} to <False>.
        - Else:
            - Writes a tarball containing the compiled CWE tests to
              <${buildDir}/${tarballName}>.
            - Sets ${sendTarballToTarget} to <True>.
    """
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
    """
    Cross compile a CWE test for FreeRTOS.

    ARGUMENTS:
    ----------
        test : String
            Test C file to compile.

        vulClass : String
            Vulnerability class <test> belongs to.

        part : Int
            Test part to build.  Passed to test as the #define directive
            <BESSPIN_TEST_PART>.

        testLogFile : String
            Unused by this function.  It exists as a parameter to enable calling
            this function with the argument <*getSetting('currentTest')>.

    SIDE-EFFECTS:
    -------------
        - Copies test build files to ${buildDir}/<vulClass>
        - Cross compiles part <part> of <test> belonging to <vulClass>.
        - Removes intermediate build artificats (such as .o files) from
          ${buildDir}.
    """
    if (part==0):
        logging.debug(f"buildFreeRTOSTest: <{test}> is called with [part=0]. Skipping the build.")
        return

    buildDir = getSetting('buildDir')
    
    # copy the test files
    vTestsDir = os.path.join(buildDir, vulClass)
    testFiles = [test, f'main_{test}', 'testsParameters.h', 'envBesspin.mk']

    for testFile in testFiles:
        cp (os.path.join(vTestsDir,testFile), buildDir)

    fPars = ftOpenFile(os.path.join(buildDir,'testsParameters.h'),'a')
    fPars.write(f"\n#define BESSPIN_TEST_PART {part}\n")
    fPars.close()

    # Build
    if ((vulClass == "informationLeakage") 
            and (test.split(".c")[0] not in getSettingDict("informationLeakage","nonstandardTests"))):
        testInfo = os.path.splitext(os.path.basename(test))[0].split("_")[1:]
        if (len(testInfo) != 3):
            logAndExit(f"buildFreeRTOSTest: Failed to parse the name of {test}.",exitCode=EXIT.Dev_Bug)
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
