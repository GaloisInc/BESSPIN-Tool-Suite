"""
Building CWEs Evaluation
"""

import glob
import os, re

from fett.base.utils.misc import *
from fett.cwesEvaluation.tests.bufferErrors.generateTests.generateTests import generateTests
from fett.cwesEvaluation.templateFreeRTOS import templateFreeRTOS
from fett.cwesEvaluation.common import isTestEnabled
from fett.target.build import freeRTOSBuildChecks, buildFreeRTOS, crossCompileUnix, cleanDirectory
from fett.cwesEvaluation.tests.PPAC.freertos import prepareFreeRTOSforPPAC

@decorate.debugWrap
def buildCwesEvaluation():
    # TODO: Generalize
    # TODO: Add support for custom build options and custom makefiles

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
            configHfile = ftOpenFile (os.path.join(getSetting('buildDir'),'fettUserConfig.h'),'a')
            configHfile.write(f"#define BIN_SOURCE_{getSetting('binarySource').replace('-','_')}\n")
            configHfile.close()

            cp (os.path.join(getSetting('repoDir'),'fett','cwesEvaluation','utils','lmcoMiscFreeRTOS.c'),
                getSetting('buildDir'))
        else:
            touch(os.path.join(getSetting('buildDir'), "fettUserConfig.h"))
        touch(os.path.join(getSetting('buildDir'), "fettFreeRTOSConfig.h"))

        if (isEnabled('useCustomCompiling') and isEnabledDict('customizedCompiling','useCustomMakefile')):
            cp (getSettingDict('customizedCompiling','pathToCustomMakefile'),
                os.path.join(getSetting('buildDir'), 'Makefile'))


    # Copy apps over
    additionalFiles = []
    for vulClass in getSetting('vulClasses'):
        # Create class dir and build
        vulClassDir = os.path.join(buildDir, vulClass)
        mkdir(vulClassDir)

        if vulClass == 'bufferErrors':
            cp (os.path.join(getSetting('repoDir'),'fett','cwesEvaluation','tests',
                                    vulClass,'envFett.mk'), vulClassDir)
            # Generate test sources
            generateTests(vulClassDir)
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
        else:
            sourcesDir = os.path.join(getSetting('repoDir'),'fett','cwesEvaluation','tests',
                                    vulClass, 'sources')
            cp (os.path.join(sourcesDir,'envFett.mk'), vulClassDir)
            for test in glob.glob(os.path.join(sourcesDir, "test_*.c")):
                # Check if the test should be skipped:
                cTestName = os.path.basename(test)
                if (isTestEnabled(vulClass,cTestName)):
                    cp (test, vulClassDir)
                else:
                    printAndLog(f"buildCwesEvaluation: Skipping <{vulClass}:{cTestName}>. It is not enabled.",doPrint=False)

        if (not isEqSetting('osImage', 'FreeRTOS')):
            # copy makefile over
            if (isEnabled('useCustomCompiling') and isEnabledDict('customizedCompiling','useCustomMakefile')):
                cp (getSettingDict('customizedCompiling','pathToCustomMakefile'),
                    os.path.join(vulClassDir, 'Makefile'))
            else: # Use default environment
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
                                'defaultEnvLinux.mk'),
                    vulClassDir)

        # Write the extra testsParameters.h
        fHeader = ftOpenFile(os.path.join(vulClassDir, "testsParameters.h"), 'w')
        # TODO: The randomizeParameters
        for xSetting, xVal in getSetting(vulClass).items():
            if (xSetting.startswith('test_')):
                settingName = xSetting.split('test_')[-1]
                fHeader.write(f"#define {settingName} {xVal}\n")
        if vulClass == "PPAC":
            fHeader.write(
                    f'#define SPOOFING_IP "{getSettingDict("PPAC", "spoofingIP")}"\n'
                    f'#define TCP_PORT_NUMBER {getSetting("fpgaPortTarget")}\n')

            if isEqSetting('osImage', 'FreeRTOS'):
                prepareFreeRTOSforPPAC(fHeader)
            else:
                pattern = os.path.join(sourcesDir,
                                       f'*_{getSetting("osImage")}')
                for source in glob.glob(pattern):
                    suffixLen = len(getSetting('osImage')) + 1
                    outFile = os.path.join(
                            vulClassDir,
                            os.path.basename(source)[:-suffixLen])
                    cp(source, outFile)
                    additionalFiles.append(outFile)

        fHeader.close()

        if isEqSetting('osImage', 'FreeRTOS'):
            prepareFreeRTOS(vulClassDir)
        elif getSetting('osImage') in ['debian', 'FreeBSD']:
            crossCompileUnix(vulClassDir,extraString=f'{vulClass} tests')
        else:
            logAndExit("<buildCwesEvaluation> is not implemented for "
                       f"<{getSetting('osImage')}>.",
                       exitCode=EXIT.Implementation)

    if getSetting('osImage') in ['debian', 'FreeBSD']:
        buildTarball(additionalFiles)


@decorate.debugWrap
@decorate.timeWrap
def buildTarball(additionalFiles):
    fileList = [(os.path.basename(f), f) for f in
                glob.glob(os.path.join(getSetting('buildDir'),
                                       "*",
                                       "*.riscv"))]
    enabledCwesEvaluations = {}
    for (test, path) in fileList:
        vulClass = os.path.basename(os.path.split(path)[0])
        try:
            enabledCwesEvaluations[vulClass].append(test)
        except KeyError:
            enabledCwesEvaluations[vulClass] = [test]
    setSetting('enabledCwesEvaluations', enabledCwesEvaluations)

    fileList += [(os.path.basename(f), f) for f in additionalFiles]

    # TODO: Do I need this += part here?  I thought it would capture the
    # entropy thing, but it looks like it doesn't?
    fileList += [(os.path.basename(f), f) for f in
                 glob.glob(os.path.join(getSetting("buildDir"), "*.riscv"))]
    tar(os.path.join(getSetting("buildDir"), getSetting('tarballName')),
        fileList)
    setSetting('sendTarballToTarget', True)

    # TODO: Put this somewhere else, use it to determine what to compile, and
    # maybe rename it

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOS(directory):
    # TODO: Just inline this function if its just a one liner
    # Generate main files
    templateFreeRTOS(directory)

@decorate.debugWrap
@decorate.timeWrap
def buildFreeRTOSTest(test, vulClass, part, testLogFile):
    # TODO: Some options in target.build.prepareFreeRTOS are omitted here

    buildDir = getSetting('buildDir')
    
    # copy the test files
    vTestsDir = os.path.join(buildDir, vulClass)
    testFiles = [test, f'main_{test}', 'testsParameters.h', 'envFett.mk']
    #Check for extra files
    if (vulClass=='PPAC'):
        extraFile = os.path.join(buildDir,'lib_PPAC','extraSources',test.replace('.c','_extra.c'))
        if (os.path.isfile(extraFile)):
            cp (extraFile,vTestsDir)
            testFiles.append(test.replace('.c','_extra.c')) 

    for testFile in testFiles:
        cp (os.path.join(vTestsDir,testFile), buildDir)

    fPars = ftOpenFile(os.path.join(buildDir,'testsParameters.h'),'a')
    fPars.write(f"\n#define TESTGEN_TEST_PART {part}\n")
    if (vulClass=='PPAC'):
        try:
            testNum = re.findall(r'\d+',test)[0]
        except Exception as exc:
            logAndExit(f"Failed to extract TESTNUM from <{test}>",exc=exc,exitCode=EXIT.Dev_Bug)
        fPars.write(f"#define TESTNUM {testNum}\n")
    fPars.close()

    # Build
    buildFreeRTOS(doPrint=False)

    #remove the current test files
    for testFile in testFiles:
        os.remove(os.path.join(buildDir,testFile))
    #remove the object files
    cleanDirectory (buildDir,endsWith='.o')
