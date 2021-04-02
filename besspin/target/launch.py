#! /usr/bin/env python3
""" 
The main file to start launching besspin
"""

from besspin.base.utils.misc import *
from besspin.target.build import prepareOsImage
from besspin.target import common
from besspin.target import vcu118
from besspin.target import qemu
from besspin.target import awsf1
from besspin.base.utils.aws import uploadToS3
from besspin.fett.build import buildApps
from besspin.cwesEvaluation.build import buildCwesEvaluation, buildFreeRTOSTest
from besspin.cwesEvaluation.common import runTests
from besspin.cwesEvaluation.freeRTOS import runFreeRTOSCwesEvaluation
from besspin.cwesEvaluation.utils.checkValidScores import checkValidScores
from besspin.cwesEvaluation.utils.computeBesspinScale import computeBesspinScale
from besspin.cwesEvaluation.utils.computeNaiveCWEsTally import computeNaiveCWEsTally
from besspin.cyberPhys.build import buildCyberPhys
from besspin.cyberPhys.run import runCyberPhys
import besspin.cyberPhys.launch
import sys, os
from importlib.machinery import SourceFileLoader

""" This is the BESSPIN entry function """
@decorate.debugWrap
@decorate.timeWrap
def startBesspin (targetId=None):
    processor = getSetting('processor',targetId=targetId)
    binarySource = getSetting('binarySource',targetId=targetId)
    osImage = getSetting('osImage',targetId=targetId)
    target = getSetting('target',targetId=targetId)
    sourceVariant = getSetting('sourceVariant',targetId=targetId)

    # ------- Global/Misc sanity checks
    if (isEqSetting('mode','fettProduction') and isEnabled('openConsole')):
        logAndExit(f"<openConsole> is not compatible with <fettProduction> mode.",exitCode=EXIT.Configuration)

    # --------   binarySource-Processor-osImage-PV Matrix --------
    # Check that the processor is provided by this team
    if (processor not in getSettingDict('besspinMatrix',[binarySource])):
        logAndExit(f"{processor} is not compatible with <{binarySource}>.",exitCode=EXIT.Configuration)
    # Check that osImage is provided for this team-processor combination
    if (osImage not in getSettingDict('besspinMatrix',[binarySource,processor])):
        logAndExit(f"{osImage} is not compatible with <{binarySource}-{processor}>.",exitCode=EXIT.Configuration)
    # check the AWS variant
    if (target=='awsf1'):
        pvAWS = getSettingDict('besspinMatrix',[binarySource,processor,osImage]) 
        if (pvAWS == 'notOnAWS'):
            logAndExit(f"<awsf1> target is not compatible with <{binarySource}-{processor}-{osImage}>.",exitCode=EXIT.Configuration)
        elif (pvAWS not in ['firesim', 'connectal', 'awsteria']):
            logAndExit(f"<{pvAWS}> is not a valid AWS PV.",exitCode=EXIT.Dev_Bug)
        elif (pvAWS in ['awsteria']):
            logAndExit(f"<{pvAWS}> PV is not yet implemented.",exitCode=EXIT.Implementation)
        setSetting('pvAWS',pvAWS,targetId=targetId)
    # Some not implemented scoring features on qemu
    if (isEqSetting('mode','evaluateSecurityTests') and isEnabled('useCustomScoring') and (target=='qemu')):
        for listOption in ['gdbKeywords','funcCheckpoints']:
            if (len(getSettingDict('customizedScoring',listOption))>0):
                warnAndLog(f"customizedScoring: <{listOption}> is not implemented on qemu.")
        if (getSettingDict('customizedScoring','memAddress')>=0):
            warnAndLog(f"customizedScoring: <memAddress> is not implemented on qemus.")
    # check the variants compatibility
    if ((sourceVariant in ['purecap','temporal']) and (binarySource!='SRI-Cambridge')):
        logAndExit(f"<{sourceVariant}> variant is not compatible with <{binarySource}>.",exitCode=EXIT.Configuration)
    if ( (sourceVariant in ['combo-100','combo-015-017-100-101-103']) 
            and ( not ((binarySource=='LMCO') and (target=='vcu118') and (processor=='chisel_p2')) ) ):
        logAndExit(f"<{sourceVariant}> variant is not compatible with <{binarySource}/{processor}/{target}>.",
            exitCode=EXIT.Configuration)
    if ((sourceVariant=='default') and (binarySource=='LMCO') and (target=='vcu118') and (processor=='chisel_p2')):
        logAndExit(f"<sourceVariant> has to be explicitly defined for <LMCO/chisel_p2/vcu118>.",
            exitCode=EXIT.Configuration)

    #qemu on Busybox
    if ((osImage=='busybox') and (target=='qemu')):
        logAndExit (f"Qemu is not implemented for {osImage}.",exitCode=EXIT.Implementation)

    # qemu on FreeRTOS
    if ((osImage=='FreeRTOS') and (target=='qemu') 
        and (not isEqSetting('mode', 'evaluateSecurityTests'))):
        logAndExit(f"Qemu is not implemented for <{getSetting('mode')}> "
                   f"mode on <{osImage}>",
                   exitCode=EXIT.Implementation)

    # Check settings for evaluateSecurityTests on qemu
    if (isEqSetting('mode', 'evaluateSecurityTests') and (target=='qemu')):
        if ((osImage=='FreeRTOS') and
            not isEqSetting('cross-compiler', 'GCC')):
            warnAndLog("<cross-compiler> setting "
                       f"<{getSetting('cross-compiler')}> is unsupported for "
                       f"<{getSetting('mode')}> mode on target "
                       f"<{target}> with osImage "
                       f"<{osImage}>.  Setting <cross-compiler> "
                       "and <linker> to <GCC>.")
            setSetting("cross-compiler", "GCC")
            setSetting("linker", "GCC")

    # Check gdbDebug sanity
    if (isEnabled('gdbDebug') and (not isEnabled('openConsole'))):
        warnAndLog("<gdbDebug> is enabled, but <openConsole> is not. <gdbDebug> will be ignored.")
        setSetting('gdbDebug',False)
    if (isEnabled('gdbDebug') and not ( (target=='vcu118') or
                                    ((target=='awsf1') and (pvAWS in ['firesim','connectal']))
                                )):
        targetName = target if (target!='awsf1') else f"aws:{pvAWS}"
        logAndExit(f"<gdbDebug> is not implemented on <{targetName}> .",exitCode=EXIT.Implementation)

    # prepare the environment
    prepareEnv(targetId=targetId)

    if (isEqSetting('mode', 'evaluateSecurityTests') and (osImage=='FreeRTOS')):
        # Run the tool in a loop when evaluating security tests on FreeRTOS
        runFreeRTOSCwesEvaluation()
        return None

    # launch besspin
    xTarget = launchBesspin(targetId=targetId)

    if (getSetting('mode') in ['fettTest', 'fettProduction']):
        mkdir (os.path.join(getSetting('workDir'),'extraArtifacts'),addToSettings='extraArtifactsPath')
        
        # Start on-line logging
        if ((osImage in ['debian', 'FreeBSD']) and (target=='awsf1')): 
            awsf1.startRemoteLogging (xTarget)
    elif (isEqSetting('mode','cyberPhys')):
        setSetting('targetObj',xTarget,targetId=targetId)
        setSetting('isUartPiped',False,targetId=targetId)
        setSetting('isTtyLogging',False,targetId=targetId)

    # Pipe UART to the network
    if (isEqSetting('mode','fettProduction')):
        awsf1.startUartPiping(xTarget) # Shoud not execute any command after piping start

    return xTarget


""" This is the prepare function before launch (binaries, network,) """ 
@decorate.debugWrap
def prepareEnv (targetId=None):
    targetInfo = f"<target{targetId}>: " if (targetId) else ''
    printAndLog (f"{targetInfo}Preparing the environment...")
    osImage = getSetting('osImage',targetId=targetId)
    target = getSetting('target',targetId=targetId)

    # config sanity checks for building artifacts
    if (osImage in ['FreeRTOS', 'debian', 'FreeBSD']):
        setSetting('bootTest',False,targetId=targetId)

        if isEqSetting("mode", "evaluateSecurityTests"):
            isThereAnythingToRun = buildCwesEvaluation()
            if (not isThereAnythingToRun):
                logAndExit("Running in <evaluateSecurityTests> mode, but no tests are enabled.",exitCode=EXIT.Nothing_to_do)
        elif isEqSetting("mode", "cyberPhys"):
            buildCyberPhys(targetId=targetId)
        elif (getSetting("mode") in ["fettTest", "fettProduction"]):
            buildApps ()
    elif (osImage=='busybox'):
        printAndLog(f"{targetInfo}<busybox> is only used for smoke testing the target/network. No applications are supported.")
        setSetting('bootTest',True,targetId=targetId)
        if (isEqSetting("mode", "evaluateSecurityTests")):
            setSetting("isThereAReasonToBoot",True) #boot to test
    else:
        logAndExit (f"<launch.prepareEnv> is not implemented for <{osImage}>.",exitCode=EXIT.Dev_Bug)

    if not (isEqSetting('mode', 'evaluateSecurityTests') and (osImage=='FreeRTOS')):
        prepareOsImage (targetId=targetId)

    if ( isEqSetting('mode', 'evaluateSecurityTests') and
            ((osImage=='FreeRTOS') or (not isEnabled('isThereAReasonToBoot'))) ):
        pass #No need to do any more preparation
    elif (target=='vcu118'):
        vcu118.resetEthAdaptor()
        vcu118.programBitfile(targetId=targetId)
    elif (target=='awsf1'):
        pvAWS = getSetting('pvAWS',targetId=targetId)
        if (pvAWS=='firesim'):
            awsf1.prepareFiresim()
            awsf1.removeKernelModules()
            awsf1.installKernelModules()
            awsf1.configTapAdaptor()
            awsf1.programAFI()
        elif (pvAWS=='connectal'):
            awsf1.prepareConnectal()
            awsf1.configTapAdaptor()
            ## remove modules because sometimes kernel panics if the modules are loaded while programming the FPGA
            awsf1.removeKernelModules()
            awsf1.programAFI()
            ## remove the modules again because the AMI has xocl in /lib/modules and it is getting auto loaded
            awsf1.removeKernelModules()
            awsf1.installKernelModules()
        else:
            logAndExit (f"<launch.prepareEnv> is not implemented for <AWS:{pvAWS}>.",exitCode=EXIT.Implementation)
    elif (target=='qemu'):
        qemu.configTapAdaptor(targetId=targetId)
    printAndLog (f"{targetInfo}Environment is ready.")

""" This is the loading/booting function """
@decorate.debugWrap
@decorate.timeWrap
def launchBesspin (targetId=None):
    try:
        xTarget = getClassType(targetId=targetId)(targetId=targetId)
    except Exception as exc:
        logAndExit (f"launchBesspin: Failed to instantiate the target class.",exc=exc,exitCode=EXIT.Dev_Bug)
    if (isEqSetting('mode', 'evaluateSecurityTests') and
        isEqSetting('osImage', 'FreeRTOS',targetId=targetId)):
        # Build the image for the upcoming test
        buildFreeRTOSTest(*getSetting("currentTest"))
    else:
        printAndLog (f"Launching BESSPIN <{getSetting('mode')} mode>...",doPrint=(not isEqSetting('mode','cyberPhys')))
    xTarget.start()
    if (isEnabled('isUnix',targetId=targetId) and (xTarget.osHasBooted)):
        if ((getSetting('osImage',targetId=targetId) in ['debian','FreeBSD']) #don't do it for busybox
                and (   (getSetting('mode') in ['fettTest', 'fettProduction'])
                        or isEqSetting('binarySource','SRI-Cambridge',targetId=targetId) #Have to change pw if SRI-Cambridge
                    )
            ): #no need to change pw in evaluation mode
            xTarget.changeRootPassword()
        if (getSetting('mode') in ['fettTest', 'fettProduction']):
            xTarget.createUser()
    if (not isEnabled('bootTest',targetId=targetId)): #actual run
        if isEqSetting('mode', 'evaluateSecurityTests'):
            sendTimeout = 20*len(getSetting('vulClasses'))
            if (('bufferErrors' in getSetting('vulClasses')) and (getSettingDict('bufferErrors','nTests')>100)):
                sendTimeout += 20*int(getSettingDict('bufferErrors','nTests')/100) #add 20 sec for each extra 100 (ceiled)
            if ((isEqSetting('target','vcu118') and isEqSetting('procFlavor','bluespec')) 
                    or isEqSetting('binarySource','SRI-Cambridge')):
                sendTimeout *= 2
            runTests(xTarget, sendFiles=isEnabled('sendTarballToTarget'), 
                timeout=sendTimeout)
        elif (getSetting('mode') in ['fettTest', 'fettProduction']):
            xTarget.runFettApps(sendFiles=isEnabled('sendTarballToTarget',targetId=targetId))
        elif (isEqSetting('mode','cyberPhys')):
            runCyberPhys(xTarget)
    if (getSetting('mode') in ['fettTest', 'fettProduction']):
        if (isEnabled('isUnix',targetId=targetId) and isEnabled("useCustomCredentials")):
            xTarget.changeUserPassword()
        if isEnabled('isUnix',targetId=targetId) and isEnabled("rootUserAccess"):
            xTarget.enableRootUserAccess()

    return xTarget

""" This is the teardown function """
@decorate.debugWrap
def endBesspin (xTarget,isDeadProcess=False):
    if (isEqSetting('mode','fettProduction')):
        awsf1.endUartPiping(xTarget)

    if (getSetting('mode') in ['fettTest', 'fettProduction']):
        if ((not isEnabled('bootTest')) and (not isDeadProcess)): #Cannot collect local logs if deadProcess
            xTarget.collectLogs()

        if ((getSetting('osImage') in ['debian', 'FreeBSD']) and (isEqSetting('target','awsf1'))): 
            collectRemoteLogging (logAndExit,getSetting,sudoShellCommand)
    
    if not ((isEqSetting('mode', 'evaluateSecurityTests') and isEqSetting('osImage', 'FreeRTOS')) 
            or (isDeadProcess)):
        if (xTarget.osHasBooted):
            xTarget.shutdown()
    
    if (isEqSetting('mode','fettProduction')):
        tarballPath = tarArtifacts (logAndExit,getSetting)
        uploadToS3(getSetting(f'{getSetting("besspinEntrypoint")}S3Bucket'), logAndExit, 
                        tarballPath, 'besspin/production/artifacts/')
        printAndLog(f"Artifacts tarball uploaded to S3.")
    elif (isEqSetting('mode', 'evaluateSecurityTests')):
        checkValidScores()
        if (isEnabled('computeNaiveCWEsTally')):
            computeNaiveCWEsTally()
        if (isEnabled('computeBesspinScale')):
            computeBesspinScale()

""" This resets the target without changing the .img + without deployment tests """
@decorate.debugWrap
@decorate.timeWrap
def resetTarget (curTarget):
    targetId = curTarget.targetId
    if ((isEqSetting('mode','fettProduction') and (not isEqSetting('target','awsf1')))
            or (not isEqSetting('mode','cyberPhys'))):
        logAndExit(f"<resetTarget> is not compatible with <{getSetting('target',targetId=targetId)}> target"
            f" in <{getSetting('mode')}> mode.")
    """
    A big decision here is whether to collectLogs and shutdown or just tear it down.
    We'll assume smth is wrong with the target, so we'll just tear it down.
    collectLogs can err in any step, no need for crazy error handling, especially that we rsyslog them anyway.
    """
    printAndLog("resetTarget: tearing down the current target...",doPrint=(not isEqSetting('mode','cyberPhys')))
    if (isEqSetting('mode','fettProduction')):
        awsf1.endUartPiping(curTarget)
    elif (isEqSetting('mode','cyberPhys')):
        besspin.cyberPhys.launch.endUartPiping(targetId)
        besspin.cyberPhys.launch.stopTtyLogging(targetId)
    curTarget.tearDown() 
    rootPassword = curTarget.rootPassword
    portsBegin = curTarget.portsBegin
    userCreated = curTarget.userCreated
    del curTarget

    printAndLog("resetTarget: Re-preparing the environment...",doPrint=(not isEqSetting('mode','cyberPhys')))
    # Reload the FPGA
    if (isEqSetting('mode','fettProduction')): #The AWS resetting need to be tested/adjusted if desired on cyberPhys
        if (isEqSetting('pvAWS','firesim')):
            awsf1.removeKernelModules()
            awsf1.installKernelModules()
            awsf1.programAFI()
        elif (isEqSetting('pvAWS', 'connectal')):
            awsf1.removeKernelModules()
            awsf1.programAFI()
            awsf1.removeKernelModules()
            awsf1.installKernelModules()
        else:
            logAndExit (f"<resetTarget> is not implemented for <AWS:{getSetting('pvAWS')}>.",exitCode=EXIT.Implementation)
    elif (isEqSetting('mode','cyberPhys')):
        if (isEqSetting('target','qemu',targetId=targetId)):
            qemu.configTapAdaptor(targetId=targetId)
        elif (isEqSetting('target','vcu118',targetId=targetId)):
            if (isEnabled('programBitfileOnReset')):
                vcu118.programBitfile(targetId=targetId)
            vcu118.resetEthAdaptor()
        else:
            logAndExit (f"<resetTarget> is not implemented for <{getSetting('target',targetId=targetId)}>."
                f"in <cyberPhys> mode.",exitCode=EXIT.Implementation)

    printAndLog("resetTarget: Re-launching...",doPrint=(not isEqSetting('mode','cyberPhys')))
    try:
        newTarget = getClassType(targetId=targetId)(targetId=targetId)
        setSetting('targetObj',newTarget,targetId=targetId)
    except Exception as exc:
        logAndExit (f"resetTarget: Failed to instantiate the target class.",exc=exc,exitCode=EXIT.Dev_Bug)

    # Adjust the needed members for reset
    newTarget.restartMode = True
    if (isEqSetting('target','awsf1',targetId=targetId)):
        newTarget.rootPassword = rootPassword
    newTarget.portsBegin = portsBegin
    newTarget.userCreated = userCreated

    newTarget.start()
    if (isEqSetting('mode','fettProduction')):
        awsf1.startUartPiping(newTarget)
    elif (isEqSetting('mode','cyberPhys')):
        if (isEnabled('pipeTheUart')):
            besspin.cyberPhys.launch.startUartPiping(targetId)
        else:
            besspin.cyberPhys.launch.startTtyLogging(targetId)

    if ((getSetting('target',targetId=targetId) in ['vcu118', 'qemu']) #We currently do not use a separate .img file
            and (isEnabled('isUnix',targetId=targetId)) 
            and (getSetting('mode') in ['fettTest', 'fettProduction'])):
        newTarget.createUser()
        if (getSetting('osImage',targetId=targetId) in ['debian','FreeBSD']):
            newTarget.changeRootPassword()
            if (isEnabled("useCustomCredentials")):
                newTarget.changeUserPassword()
            if (isEnabled("rootUserAccess")):
                newTarget.enableRootUserAccess()

    if (isEqSetting('mode','cyberPhys') and (not isEnabled('bootTest',targetId=targetId))):
        runCyberPhys(newTarget)

    return newTarget

""" This decides the classes hierarchy """
@decorate.debugWrap
def getClassType(targetId=None):
    # This function gets executed in try/except
    def errorAndRaise(message,exc=None):
        errorAndLog(message,exc=exc)
        raise
    if (isEqSetting('target','awsf1',targetId=targetId)):
        return getattr(awsf1,f"{getSetting('pvAWS',targetId=targetId)}Target")
    elif (isEqSetting('target','qemu',targetId=targetId)):
        return qemu.qemuTarget
    elif (isEqSetting('target','vcu118',targetId=targetId)):
        return vcu118.vcu118Target
    else:
        errorAndRaise (f"<launch.getClassType> is not implemented for <{getSetting('target',targetId=targetId)}>.")


