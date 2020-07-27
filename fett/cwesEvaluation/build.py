"""
Building CWEs Evaluation
"""

import glob
import os

from fett.base.utils.misc import *
from fett.cwesEvaluation.templateFreeRTOS import templateFreeRTOS
import fett.target.build


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


    # Copy apps over
    for vulClass in getSetting('vulClasses'):
        # Create class dir and build
        vulClassDir = os.path.join(buildDir, vulClass)
        mkdir(vulClassDir)
        cp(os.path.join(getSetting('repoDir'),
                        'fett',
                        'cwesEvaluation',
                        'tests',
                        vulClass,
                        'sources'),
            vulClassDir,
            "*.c")
        cp(os.path.join(getSetting('repoDir'),
                        'fett',
                        'target',
                        'utils',
                        'Makefile.xcompileDir'),
           os.path.join(vulClassDir, 'Makefile'))
        cp(os.path.join(getSetting('repoDir'),
                        'fett',
                        'cwesEvaluation',
                        'tests',
                        'scripts',
                        'emulation',
                        'defaultEnvLinux.mk'),
            vulClassDir)

        testsParametersHeader = os.path.join(vulClassDir, "testsParameters.h")
        if vulClass == "resourceManagement":
            # Write configuration header file
            # TODO: Write this based on values in the config file.  You'll also
            # have to change it based on the suite being run.  Lastly, it
            # doesn't seem to exist for all classes of vulnerabilities.
            with ftOpenFile(os.path.join(testsParametersHeader), 'w') as f:
                f.write("#define nResourceLimit 10\n")
        elif vulClass == "numericErrors":
            # Write empty configuration header file (nothing to configure)
            ftOpenFile(testsParametersHeader, 'w').close()

        if isEqSetting('osImage', 'FreeRTOS'):
            prepareFreeRTOS(vulClassDir)
        elif getSetting('osImage') in ['debian', 'FreeBSD']:
            crossCompileUnix(vulClassDir)
        else:
            logAndExit("<buildCwesEvaluation> is not implemented for "
                       f"<{getSetting('osImage')}>.",
                       exitCode=EXIT.Implementation)

    if getSetting('osImage') in ['debian', 'FreeBSD']:
        buildTarball()


@decorate.debugWrap
@decorate.timeWrap
def buildTarball():
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
def crossCompileUnix(directory):
    #cross-compiling sanity checks
    if ((not isEqSetting('cross-compiler','Clang')) and isEqSetting('linker','LLD')):
        # TODO: Is this true for testgen?
        warnAndLog (f"Linking using <{getSetting('linker')}> while cross-compiling with <{getSetting('cross-compiler')} is not supported. Linking using <GCC> instead.>.")
        setSetting('linker','GCC')

    printAndLog (f"Cross-compiling ...")
    envLinux = []
    osImageCap1 = getSetting('osImage')[0].upper() + getSetting('osImage')[1:]
    envLinux.append(f"OS_IMAGE={osImageCap1}")
    envLinux.append(f"BACKEND={getSetting('target').upper()}")
    envLinux.append(f"COMPILER={getSetting('cross-compiler').upper()}")
    envLinux.append(f"LINKER={getSetting('linker').upper()}")
    logging.debug(f"going to make using {envLinux}")
    make(envLinux, directory)
    printAndLog(f"Files cross-compiled successfully.")


@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOS(directory):
    # TODO: Just inline this function if its just a one liner
    # Generate main files
    templateFreeRTOS(directory)

@decorate.debugWrap
@decorate.timeWrap
def buildFreeRTOSTest(test, vulClass, part):
    # TODO: Some options in target.build.prepareFreeRTOS are omitted here

    fett.target.build.freeRTOSBuildChecks()

    # Remove all files, but not folders, from build directory
    for f in os.listdir(getSetting('buildDir')):
        path = os.path.join(getSetting('buildDir'), f)
        try:
            os.remove(path)
        except IsADirectoryError:
            pass
        except Exception as exc:
            logAndExit(f'<buildFreeRTOSTest> Failed to remove <{path}>',
                       exc=exc,
                       exitCode=EXIT.Files_and_paths)

    #copy the C files, .mk files, and any directory
    copyDir(os.path.join(getSetting('repoDir'),'fett','target','srcFreeRTOS'),
            getSetting('buildDir'),
            copyContents=True)
    # Remove existing main file
    os.remove(os.path.join(getSetting('buildDir'), "main_fett.c"))

    cp(os.path.join(getSetting('repoDir'),
                    'fett',
                    'target',
                    'srcFreeRTOS'),
       getSetting('buildDir'),
       pattern="*.h")  # TODO: Do I really want ALL of these headers?
    # TODO: it feels silly to copy from a subdir to the build dir like this
    cp(os.path.join(getSetting('buildDir'), vulClass),
       getSetting('buildDir'),
       pattern=f"*{test}")
    cp(os.path.join(getSetting('buildDir'), vulClass),
       getSetting('buildDir'),
       pattern=f"*.h")


    # TODO: Put listConfigParams back in to fill the header file?
    # Write empty fett configuration header file (nothing to configure)
    ftOpenFile(os.path.join(getSetting('buildDir'), "fettUserConfig.h"), 'w').close()

    fett.target.build.prepareFreeRTOSNetworkParameters()

    # TODO: Should probably modify the source files to support AWS instead of
    # this hack
    backend = ("FPGA" if isEqSetting("target", "aws")
                      else getSetting("target").upper())

    # Define variables testgen uses
    with ftOpenFile(os.path.join(getSetting('buildDir'), 'envFett.mk'), 'a') as mk:
        mk.write("CFLAGS += "
                 "-DtestgenOnFreeRTOS "
                 f"-Dtestgen{backend} "
                 f"-DTESTGEN_TEST_PART={part}")

    # Build
    fett.target.build.buildFreeRTOS()
