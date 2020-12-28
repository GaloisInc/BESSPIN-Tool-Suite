#! /usr/bin/env python3
"""
Building apps
"""

from fett.base.utils.misc import *
from fett.base.utils.ssl import gen_cert
from fett.apps.freertos import freertos
import fett.target.build
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
        cp(os.path.join(targetUtilsDir,'defaultEnvUnix.mk'),getSetting('buildDir'))

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

@decorate.debugWrap
@decorate.timeWrap
def prepareFreeRTOS():
    """
    We have three different sources of FreeRTOS here:
    1. If 'buildApps' is enabled --> Compile it.
    2. If 'buildApps' is disabled && useCustomImage is disabled --> Nix
    3. If 'buildApps' is disabled && useCustomImage is enabled --> customImage
    """

    #Netboot on FreeRTOS?
    if (isEqSetting('osImage','FreeRTOS') and isEqSetting('elfLoader','netboot')):
        warnAndLog (f"Netboot cannot load FreeRTOS image. Falling to JTAG.", doPrint=False)
        setSetting('elfLoader','JTAG')

    # define some paths
    osImageAsm = os.path.join(getSetting('osImagesDir'),f"{getSetting('osImage')}.asm")
    setSetting('osImageAsm',osImageAsm)

    if (not isEnabled('buildApps')): #just fetch the image
        fett.target.build.importImage()
    else: #build it
        fett.target.build.freeRTOSBuildChecks()

        #copy the C files, .mk files, and any directory
        copyDir(os.path.join(getSetting('repoDir'),'fett','apps','freertos','srcMain'),getSetting('buildDir'),copyContents=True)

        #Include the relevant user configuration parameters
        #This is a list of tuples: (settingName,macroName)
        listConfigParams = [('HTTPPortTarget','HTTP_PORT'),
                            ('TFTPPortTarget','TFTP_PORT'),
                            ('debugMode','FETT_DEBUG'),
                            ('OTAMaxSignedPayloadSize','OTA_MAX_SIGNED_PAYLOAD_SIZE')]

        configHfile = ftOpenFile (os.path.join(getSetting('buildDir'),'fettUserConfig.h'),'a')
        for xSetting,xMacro in listConfigParams:
            try:
                intVal = int(getSetting(xSetting))
            except Exception as exc:
                logAndExit(f"Invalid type in populating <fettUserConfig.h>.",exc=exc,exitCode=EXIT.Dev_Bug)
            configHfile.write(f"#define {xMacro} {intVal}\n")
        #Write the ota filename too (not list as it is unique)
        configHfile.write(f"#define OTA_FILENAME \"{getSettingDict('freertosAssets',['otaHtml'])}\"\n")
        #Write the bianry source for team specific codes
        configHfile.write(f"#define BIN_SOURCE_{getSetting('binarySource').replace('-','_')}\n")
        #Translate the mode to one char: T or D
        configHfile.write(f"#define FETT_MODE \'{getSetting('mode')[0].upper()}\'\n")
        configHfile.close()

        fett.target.build.prepareFreeRTOSNetworkParameters()
        fett.target.build.buildFreeRTOS()
    return


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
        cpFilesToBuildDir (runtimeFilesDir, pattern="nginx.sh")
        tarFiles += ["nginx.sh"]
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
def getBinDir(app,targetId=None):
    return os.path.join(getSetting('binaryRepoDir'), getSetting('binarySource',targetId=targetId),
        'appsBinaries', app, getSetting('osImage',targetId=targetId))

@decorate.debugWrap
def cpFilesToBuildDir (sourceDir, pattern=None, targetId=None):
    # If no pattern is specified, look for "*.c" files if we're building,
    # otherwise *.riscv
    if pattern is None:
        pattern = "*.c" if isEnabled('buildApps') else "*.riscv"
    cp (sourceDir,getSetting('buildDir',targetId=targetId),pattern=pattern)

@decorate.debugWrap
def cpDirToBuildDir(sourceDir, targetId=None):
    copyDir(sourceDir, getSetting('buildDir', targetId=targetId))

@decorate.debugWrap
def buildDirPathTuple(path, targetId=None):
    return (path, os.path.join(getSetting('buildDir',targetId=targetId), path))
