#! /usr/bin/env python3
"""
Building apps
"""

from fett.base.utils.misc import *
from fett.base.utils.ssl import gen_cert
from fett.apps.freertos import freertos
import os

""" The entry function
---------------------------------------
"""
@decorate.debugWrap
def buildApps ():
    # create the build directory
    buildDir = os.path.join(getSetting('workDir'),'build')
    mkdir(buildDir,addToSettings='buildDir')
    mkdir(os.path.join(buildDir, "keys"))
    mkdir(os.path.join(buildDir, "certs"))

    setSetting('sendTarballToTarget',False) #any app has to enable this to send the tarball to target
    tarName = os.path.join(getSetting('buildDir'),getSetting('tarballName'))
    if (isEnabled('buildApps') and isEnabled('isUnix')):
        targetUtilsDir = os.path.join(getSetting('repoDir'),'fett','target','utils')
        cp(os.path.join(targetUtilsDir,'Makefile.xcompileDir'),os.path.join(getSetting('buildDir'),'Makefile'))
        cp(os.path.join(targetUtilsDir,'defaultEnvLinux.mk'),getSetting('buildDir'))

    if (isEqSetting('osImage','FreeRTOS')):
        buildFreeRTOSapps()
    elif (getSetting('osImage') in ['debian', 'FreeBSD']):
        buildWebserver(tarName)
        buildDatabase(tarName)
        buildVoting(tarName)
        if (getSetting('binarySource') in ['MIT']):
            buildEnclaves(tarName)
    else:
        logAndExit (f"<launch.prepareEnv> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)

"""
- FreeRTOS, building an app means copying the C files/headers/.mk env files to the workDir to prepare for os build.
- Unix: if building is disabled, then nothing to do here. If building is enabled, then we copy and compile here.
"""

# app-specific building steps -----------------------------------------------------------

""" Special building for 'freertos' """
@decorate.debugWrap
@decorate.timeWrap
def buildFreeRTOSapps():
    assetsPath = os.path.join(getSetting('repoDir'),getSettingDict('freertosAssets',['path']))
    setSetting('assetsDir',assetsPath)
    
    if (not isEnabled('buildApps')):
        pass #For readability
    else:
        appLibPath = os.path.join(getSetting('buildDir'),'appLib')
        mkdir (appLibPath,addToSettings='appLibDir')
        cp (getSourceDir('freertos'),appLibPath,pattern='*.c')
        cp (getSourceDir('freertos'),appLibPath,pattern='*.h')
        freertos.prepareAssets()        

""" Special building for 'webserver' """
@decorate.debugWrap
@decorate.timeWrap
def copyWebserverFiles(tarName):
    """
    Build a tar containing:
      - nginx
      - conf/<nginx configuration>
      - html/<html files>
      - certs/<certname>
      - keys/<keyname>
    """
    gen_cert("fett-webserver",
        os.path.join(getSetting('buildDir'), "keys"),
        os.path.join(getSetting('buildDir'), "certs")
    )

    if isEqSetting('binarySource', 'SRI-Cambridge'):
        tarFiles = ["certs", "keys"] #Only those are needed
        return map(buildDirPathTuple, tarFiles)

    cpFilesToBuildDir(getBinDir('webserver'), pattern="sbin/nginx")
    cpDirToBuildDir(os.path.join(getAppDir('webserver'), "common", "conf"))
    cpDirToBuildDir(os.path.join(getAppDir('webserver'), "common", "html"))

    tarFiles = ["nginx", "conf", "html", "certs", "keys"]

    runtimeFilesDir = os.path.join(getAppDir('webserver'), getSetting('osImage'))
    if getSetting('osImage') == 'debian':
        cpFilesToBuildDir (runtimeFilesDir, pattern="nginx.service")
        tarFiles += ["nginx.service"]
    elif getSetting('osImage') == 'FreeBSD':
        cpFilesToBuildDir (runtimeFilesDir, pattern="rcfile")
        tarFiles += ["rcfile"]
    else:
        logAndExit (f"Installing nginx is not supported on <{getSetting('osImage')}>",
                    exitCode=EXIT.Dev_Bug)
    filesList=map(buildDirPathTuple, tarFiles)
    return filesList

@decorate.debugWrap
@decorate.timeWrap
def copyDatabaseFiles(tarName):
    """
    Build a tar just containing `sqlite`
    """
    # Just grab the pre-built binary
    cpFilesToBuildDir (getBinDir('database'), pattern="sqlite")
    # Create the tarball here to be sent to target
    destBin = "sqlite"
    srcBin  = os.path.join(getSetting('buildDir'), "sqlite")
    filesList = [(destBin, srcBin)]
    return filesList

@decorate.debugWrap
@decorate.timeWrap
def copyVotingFiles(tarName):
    # sqlite binary
    # sqlFiles    = copyDatabaseFiles(tarName)
    # Nginx + config + service files
    # serverFiles = copyWebserverFiles(tarName)

    gen_cert("fett-voting",
        os.path.join(getSetting('buildDir'), "keys"),
        os.path.join(getSetting('buildDir'), "certs")
    )

    if isEqSetting('binarySource', 'SRI-Cambridge'):
        return list(map(buildDirPathTuple, ['keys','certs']))        

    cpFilesToBuildDir(getBinDir('voting'), 'bvrs')
    cpFilesToBuildDir(getBinDir('voting'), 'kfcgi')
    cpDirToBuildDir(os.path.join(getAppDir('voting'), 'common', 'conf', 'sites'))
    cpDirToBuildDir(os.path.join(getAppDir('voting'), 'common', 'static'))
    cp(os.path.join(getAppDir('voting'), "common", "conf"),
       os.path.join(getSetting('buildDir'), "conf"),
       pattern="*.conf")
    cp(os.path.join(getAppDir('voting'), "common"),
       os.path.join(getSetting('buildDir')),
       pattern="bvrs.db")

    filesList = list(map(buildDirPathTuple, ['bvrs', 'kfcgi', 'conf','keys','certs', 'bvrs.db']))
    filesList.append(('conf/sites', os.path.join(getSetting('buildDir'), 'sites')))
    filesList.append(('static', os.path.join(getSetting('buildDir'), 'static')))

    if isEqSetting('osImage', 'debian'):
        cpFilesToBuildDir(os.path.join(getAppDir('voting'), 'debian'), 'bvrs.service')
        filesList.append(buildDirPathTuple('bvrs.service'))
    elif isEqSetting('osImage', 'FreeBSD'):
        cpFilesToBuildDir(os.path.join(getAppDir('voting'), 'FreeBSD'), 'bvrs.sh')
        filesList.append(buildDirPathTuple('bvrs.sh'))
    else:
        logAndExit (f"Installing bvrs is not supported on <{getSetting('osImage')}>",
                    exitCode=EXIT.Dev_Bug)

    # Need kfcgi, webserver's nginx.conf, bvrs app
    # We should probably just generate the initial database script here
    return filesList

""" Special building for 'webserver' """
@decorate.debugWrap
@decorate.timeWrap
def copyEnclavesFiles(tarName):
    """
    Build a tar containing:
      - enclaves/lib/security/pam_enclave.so
      - enclaves/ssith/pam-enclave.bin
      - enclaves/ssith/aes-enclave.bin
      - enclaves/ssith/aes-main
      - enclaves/etc/pam.d/testing
      - install-enclaves.sh
    """
    cpDirToBuildDir(os.path.join(getBinDir('enclaves'), "enclaves"))
    cpFilesToBuildDir(getBinDir('enclaves'), pattern="install-enclaves.sh")

    tarFiles = ["enclaves", "install-enclaves.sh"]

    filesList=map(buildDirPathTuple, tarFiles)
    return filesList

@decorate.debugWrap
@decorate.timeWrap
def buildWebserver(tarName):
    if (isEnabled('buildApps')):
        logAndExit (f"Building from source is not supported for the webserver application",
                    exitCode=EXIT.Configuration)
    else:
        tarFiles = copyWebserverFiles(tarName)
        #Create the tarball here to be sent to target
        tar (tarName, tarFiles)
        setSetting('sendTarballToTarget',True)
    return

""" Special building for 'database' """
@decorate.debugWrap
@decorate.timeWrap
def buildDatabase(tarName):
    if (isEnabled('buildApps')):
        logAndExit (f"Building from source is not supported for the database application",
                    exitCode=EXIT.Configuration)
    elif isEqSetting('binarySource', 'SRI-Cambridge'):
        return
    else:
        tarFiles = copyDatabaseFiles(tarName)
        tar (tarName, filesList=tarFiles)

        setSetting('sendTarballToTarget',True)
    return

""" Special building for 'voting' """
@decorate.debugWrap
@decorate.timeWrap
def buildVoting(tarName):
    if (isEnabled('buildApps')):
        logAndExit (f"Building from source is not supported for the voting application",
                    exitCode=EXIT.Configuration)
    else:
        tarFiles = copyVotingFiles(tarName)
        tar (tarName, filesList=tarFiles)

        setSetting('sendTarballToTarget',True)
    return

@decorate.debugWrap
@decorate.timeWrap
def buildEnclaves(tarName):
    if (isEnabled('buildApps')):
        logAndExit (f"Building from source is not supported for the enclaves application",
                    exitCode=EXIT.Configuration)
    else:
        tarFiles = copyEnclavesFiles(tarName)
        #Create the tarball here to be sent to target
        tar (tarName, tarFiles)
        setSetting('sendTarballToTarget',True)
    return

# re-used parts -----------------------------------------------------------

@decorate.debugWrap
def getSourceDir (app):
    return os.path.join(getSetting('repoDir'),'fett','apps',app)

@decorate.debugWrap
def getAppDir(app):
    return os.path.join(getSetting('repoDir'),'build', app)

@decorate.debugWrap
def getBinDir(app):
    return os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource'), 'appsBinaries', app, getSetting('osImage'))

@decorate.debugWrap
def cpFilesToBuildDir (sourceDir, pattern=None):
    # If no pattern is specified, look for "*.c" files if we're building,
    # otherwise *.riscv
    if pattern is None:
        pattern = "*.c" if isEnabled('buildApps') else "*.riscv"
    cp (sourceDir,getSetting('buildDir'),pattern=pattern)

@decorate.debugWrap
def cpDirToBuildDir(sourceDir):
    copyDir(sourceDir, getSetting('buildDir'))

@decorate.debugWrap
def buildDirPathTuple(path):
    return (path, os.path.join(getSetting('buildDir'), path))

@decorate.debugWrap
@decorate.timeWrap
def crossCompileUnix():
    #cross-compiling sanity checks
    if ((not isEqSetting('cross-compiler','Clang')) and isEqSetting('linker','LLD')):
        warnAndLog (f"Linking using <{getSetting('linker')}> while cross-compiling with <{getSetting('cross-compiler')} is not supported. Linking using <GCC> instead.>.")
        setSetting('linker','GCC')

    printAndLog (f"Cross-compiling ...")
    envLinux = []
    osImageCap1 = getSetting('osImage')[0].upper() + getSetting('osImage')[1:]
    envLinux.append(f"OS_IMAGE={osImageCap1}")
    envLinux.append(f"TARGET={getSetting('target').upper()}")
    envLinux.append(f"COMPILER={getSetting('cross-compiler').upper()}")
    envLinux.append(f"LINKER={getSetting('linker').upper()}")
    logging.debug(f"going to make using {envLinux}")
    make (envLinux,getSetting('buildDir'))
    printAndLog(f"Files cross-compiled successfully.")
