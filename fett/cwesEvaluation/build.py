"""
Building CWEs Evaluation
"""

import glob
import os

from fett.base.utils.misc import *


@decorate.debugWrap
def buildCwesEvaluation():
    # TODO: Generalize
    # TODO: Even for this case, I skipped a bunch of options and just stuck
    # with the default makefile.  Do we want to support custom makefiles /
    # build options?

    # Create build directory
    buildDir = os.path.join(getSetting('workDir'), 'build')
    mkdir(buildDir, addToSettings="buildDir")

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
            with open(os.path.join(testsParametersHeader), 'w') as f:
                f.write("#define nResourceLimit 10\n")
        elif vulClass == "numericErrors":
            # Write empty configuration header file (nothing to configure)
            open(testsParametersHeader, 'w').close()



        crossCompileUnix(vulClassDir)

    # TODO: Use list comprehension to flatten tarball
    fileList = [(os.path.basename(f), f) for f in
                glob.glob(os.path.join(buildDir,"*", "*.riscv"))]

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
                 glob.glob(os.path.join(buildDir, "*.riscv"))]
    tar(os.path.join(buildDir, getSetting('tarballName')), fileList)
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
