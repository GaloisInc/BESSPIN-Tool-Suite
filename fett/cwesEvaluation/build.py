"""
Building CWEs Evaluation
"""

# TODO: Unused?
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
    logAndExit(f"<buildCwesEvaluation> not implemented", exitCode=EXIT.Dev_Bug)
