#! /usr/bin/env python3
""" 
The main file to start launching fett
"""

from fett.base.utils.misc import *
from fett.target.build import prepareOsImage
from fett.target import common
from fett.target import fpga
from fett.target import qemu
from fett.target import aws
from fett.base.utils.aws import uploadToS3
from fett.apps.build import buildApps
import sys, os
from importlib.machinery import SourceFileLoader

""" This is the FETT entry function """
@decorate.debugWrap
@decorate.timeWrap
def startFett ():
    # ------- Global/Misc sanity checks
    if (isEqSetting('mode','production') and isEnabled('openConsole')):
        logAndExit(f"<openConsole> is not compatible with production mode.",exitCode=EXIT.Configuration)

    # --------   binarySource-Processor-osImage-PV Matrix --------
    # Check that the processor is provided by this team
    if (getSetting('processor') not in getSettingDict('fettMatrix',[getSetting('binarySource')])):
        logAndExit(f"{getSetting('processor')} is not compatible with <{getSetting('binarySource')}>.",exitCode=EXIT.Configuration)
    # Check that osImage is provided for this team-processor combination
    if (getSetting('osImage') not in getSettingDict('fettMatrix',[getSetting('binarySource'),getSetting('processor')])):
        logAndExit(f"{getSetting('osImage')} is not compatible with <{getSetting('binarySource')}-{getSetting('processor')}>.",exitCode=EXIT.Configuration)
    # check the AWS variant
    if (isEqSetting('target','aws')):
        pvAWS = getSettingDict('fettMatrix',[getSetting('binarySource'),getSetting('processor'),getSetting('osImage')]) 
        if (pvAWS == 'notOnAWS'):
            logAndExit(f"<aws> target is not compatible with <{getSetting('binarySource')}-{getSetting('processor')}-{getSetting('osImage')}>.",exitCode=EXIT.Configuration)
        elif (pvAWS not in ['firesim', 'connectal', 'awsteria']):
            logAndExit(f"<{pvAWS}> is not a valid AWS PV.",exitCode=EXIT.Dev_Bug)
        elif (pvAWS in ['awsteria']):
            logAndExit(f"<{pvAWS}> PV is not yet implemented.",exitCode=EXIT.Implementation)
        setSetting('pvAWS',pvAWS)

    #qemu on FreeRTOS and Busybox
    if ((getSetting('osImage') in ['FreeRTOS','busybox']) and isEqSetting('target','qemu')):
        logAndExit (f"Qemu is not implemented for {getSetting('osImage')}.",exitCode=EXIT.Implementation)

    # prepare the environment
    prepareEnv()

    # launch fett
    xTarget = launchFett()

    mkdir (os.path.join(getSetting('workDir'),'extraArtifacts'),addToSettings='extraArtifactsPath')
    
    # Start on-line logging
    if ((getSetting('osImage') in ['debian', 'FreeBSD']) and (isEqSetting('target','aws'))): 
        aws.startRemoteLogging (xTarget)

    # Pipe UART to the network
    if (isEqSetting('mode','production')):
        aws.startUartPiping(xTarget) # Shoud not execute any command after piping start

    return xTarget


""" This is the prepare function before launch (binaries, network,) """ 
@decorate.debugWrap
def prepareEnv ():
    printAndLog (f"Preparing the environment...")
    # cannot buildApps on aws
    if (isEnabled('buildApps') and isEqSetting('target','aws') and isEqSetting('mode','production')):
        warnAndLog (f"It is not allowed to <buildApps> on <AWS> in <production> mode. This will be switched off.")
        setSetting('buildApps',False)

    # config sanity checks for building apps
    if (getSetting('osImage') in ['FreeRTOS', 'debian', 'FreeBSD']):
        setSetting('runApp',True)
        buildApps ()
    elif (isEqSetting('osImage','busybox')):
        printAndLog(f"<busybox> is only used for smoke testing the target/network. No applications are supported.")
        setSetting('runApp',False)
    else:
        logAndExit (f"<launch.prepareEnv> is not implemented for <{getSetting('osImage')}>.",exitCode=EXIT.Dev_Bug)

    prepareOsImage ()

    if (isEqSetting('target','fpga')):
        fpga.programBitfile()
        fpga.resetEthAdaptor()
    elif (isEqSetting('target','aws')):
        if (isEqSetting('pvAWS','firesim')):
            aws.prepareFiresim()
            aws.removeKernelModules()
            aws.installKernelModules()
            aws.configTapAdaptor()
            aws.programAFI()
        elif (isEqSetting('pvAWS', 'connectal')):
            aws.prepareConnectal()
            aws.configTapAdaptor()
            ## remove modules because sometimes kernel panics if the modules are loaded while programming the FPGA
            aws.removeKernelModules()
            aws.programAFI()
            ## remove the modules again because the AMI has xocl in /lib/modules and it is getting auto loaded
            aws.removeKernelModules()
            aws.installKernelModules()
        else:
            logAndExit (f"<launch.prepareEnv> is not implemented for <AWS:{getSetting('pvAWS')}>.",exitCode=EXIT.Implementation)
    printAndLog (f"Environment is ready.")

""" This is the loading/booting function """
@decorate.debugWrap
@decorate.timeWrap
def launchFett ():
    printAndLog (f"Launching FETT <{getSetting('mode')} mode>...")
    try:
        xTarget = getClassType()()
    except Exception as exc:
        logAndExit (f"launchFett: Failed to instantiate the target class.",exitCode=EXIT.Dev_Bug)
    xTarget.start()
    if (isEnabled('isUnix')):
        if (getSetting('osImage') in ['debian','FreeBSD']):
            xTarget.changeRootPassword()
        xTarget.createUser()
    if (isEnabled('runApp')):
        xTarget.runApp(sendFiles=isEnabled('sendTarballToTarget'))
    if (isEnabled('isUnix') and isEnabled("useCustomCredentials")):
        xTarget.changeUserPassword()
    if isEnabled('isUnix') and isEnabled("rootUserAccess"):
        xTarget.enableRootUserAccess()

    return xTarget

""" This is the teardown function """
@decorate.debugWrap
def endFett (xTarget):
    if (isEqSetting('mode','production')):
        aws.endUartPiping(xTarget)

    if (isEnabled('runApp')):
        xTarget.collectLogs()

    if ((getSetting('osImage') in ['debian', 'FreeBSD']) and (isEqSetting('target','aws'))): 
        collectRemoteLogging (logAndExit,getSetting,sudoShellCommand)

    xTarget.shutdown()
    
    if (isEqSetting('mode','production')):
        tarballPath = tarArtifacts (logAndExit,getSetting)
        uploadToS3(getSetting(f'{getSetting("fettEntrypoint")}S3Bucket'), logAndExit, 
                        tarballPath, 'fett-target/production/artifacts/')
        printAndLog(f"Artifacts tarball uploaded to S3.")

""" This resets the target without changing the .img + without deployment tests """
@decorate.debugWrap
@decorate.timeWrap
def resetTarget (curTarget):
    if ((not isEqSetting('target','aws')) or (not isEqSetting('mode','production'))):
        logAndExit(f"<resetTarget> is not compatible with <{getSetting('target')}> target in <{getSetting('mode')}> mode.")
    """
    A big decision here is whether to collectLogs and shutdown or just tear it down.
    We'll assume smth is wrong with the target, so we'll just tear it down.
    collectLogs can err in any step, no need for crazy error handling, especially that we rsyslog them anyway.
    """
    printAndLog("resetTarget: tearing down the current target...")
    aws.endUartPiping(curTarget)
    curTarget.targetTearDown() 
    rootPassword = curTarget.rootPassword
    del curTarget

    printAndLog("resetTarget: Re-preparing the environment...")
    # Reload the FPGA
    if (isEqSetting('pvAWS','firesim')):
        aws.removeKernelModules()
        aws.installKernelModules()
        aws.programAFI()
    elif (isEqSetting('pvAWS', 'connectal')):
        aws.removeKernelModules()
        aws.programAFI()
        aws.removeKernelModules()
        aws.installKernelModules()
    else:
        logAndExit (f"<resetTarget> is not implemented for <AWS:{getSetting('pvAWS')}>.",exitCode=EXIT.Implementation)
    
    printAndLog("resetTarget: Re-launching...")
    try:
        newTarget = getClassType()()
    except Exception as exc:
        logAndExit (f"resetTarget: Failed to instantiate the target class.",exitCode=EXIT.Dev_Bug)

    # Adjust the needed members for reset
    newTarget.restartMode = True
    newTarget.rootPassword = rootPassword
    
    newTarget.start(restartMode=True)
    aws.startUartPiping(newTarget)

    return newTarget

""" This decides the classes hierarchy """
@decorate.debugWrap
def getClassType():
    # This function gets executed in try/except
    def errorAndRaise(message,exc=None):
        errorAndLog(message,exc=exc)
        raise

    if (isEqSetting('target','aws')):
        return getattr(aws,f"{getSetting('pvAWS')}Target")
    elif (isEqSetting('target','qemu')):
        return qemu.qemuTarget
    elif (isEqSetting('target','fpga')):
        gfeTestingScripts = getSettingDict('nixEnv',['gfeTestingScripts'])
        if (gfeTestingScripts not in os.environ):
            errorAndRaise (f"<${gfeTestingScripts}> not found in the nix path.")
        try:
            sys.path.append(os.environ[gfeTestingScripts])
            from test_gfe_unittest import TestLinux, TestFreeRTOS
        except Exception as exc:
            errorAndRaise (f"Failed to load <test_gfe_unittest> from <${gfeTestingScripts}>.",exc=exc)
        if (isEqSetting('xlen',32)):
            return type('classFpgaTarget',(fpga.fpgaTarget,TestFreeRTOS),dict())
        elif(isEqSetting('xlen',64)):
            return type('classFpgaTarget',(fpga.fpgaTarget,TestLinux),dict())
        else:
            errorAndRaise (f"Invalid <xlen={getSetting('xlen')}> value.")

    else:
        errorAndRaise (f"<launch.getClassType> is not implemented for <{getSetting('target')}>.")


