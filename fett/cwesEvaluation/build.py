"""
Building CWEs Evaluation
"""

import glob
import os

from fett.apps.build import cpFilesToBuildDir
from fett.base.utils.misc import *


@decorate.debugWrap
def buildCwesEvaluation():
    # TODO: Generalize
    # TODO: Even for this case, I skipped a bunch of options and just stuck
    # with the default makefile.  Do we want to support custom makefiles /
    # build options?

    # Create build directory
    buildDir = os.path.join(getSetting('workDir'), 'build')
    mkdir(buildDir,addToSettings='buildDir')

    # Copy apps over
    # TODO: Use buildApps instead, rather than second parameter here?
    # TODO: Use os.path.join
    cpFilesToBuildDir("fett/cwesEvaluation/tests/3_ResourceManagement/sources",
                      "*.c")
    cp(os.path.join(getSetting('repoDir'),
                    'fett',
                    'target',
                    'utils',
                    'Makefile.xcompileDir'),
       os.path.join(buildDir, 'Makefile'))
    cp(os.path.join(getSetting('repoDir'),
                    'fett',
                    'cwesEvaluation',
                    'tests',
                    'scripts',
                    'emulation',
                    'defaultEnvLinux.mk'),
        buildDir)

    # Write configuration header file
    # TODO: Write this based on values in the config file.  You'll also have to
    # change it based on the suite being run.  Lastly, it doesn't seem to exist
    # for all classes of vulnerabilities.
    with open(os.path.join(buildDir, "testsParameters.h"), 'w') as f:
        f.write("#define nResourceLimit 10\n")


    crossCompileUnix()

    # TODO: Use list comprehension to flatten tarball
    fileList = [(os.path.basename(f), f) for f in
                glob.glob(os.path.join(buildDir, "*.riscv"))]
    tar(os.path.join(buildDir, getSetting('tarballName')), fileList)

    setSetting('sendTarballToTarget', True)

@decorate.debugWrap
@decorate.timeWrap
def crossCompileUnix():
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
    make (envLinux,getSetting('buildDir'))
    printAndLog(f"Files cross-compiled successfully.")
