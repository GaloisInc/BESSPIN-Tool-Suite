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
#from fett.target import aws
from fett.apps.build import buildApps
import sys, os
from importlib.machinery import SourceFileLoader

""" This is the FETT entry function """
@decorate.debugWrap
@decorate.timeWrap
def startFett ():
    # ------- Global/Misc sanity checks

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
        elif (pvAWS in ['connectal', 'awsteria']):
            logAndExit(f"<{pvAWS}> PV is not yet implemented.",exitCode=EXIT.Implementation)
        setSetting('pvAWS',pvAWS)

    #qemu on FreeRTOS and Busybox
    if ((getSetting('osImage') in ['FreeRTOS','busybox']) and isEqSetting('target','qemu')):
        logAndExit (f"Qemu is not implemented for {getSetting('osImage')}.",exitCode=EXIT.Implementation)

    # prepare the environment
    prepareEnv()

    # launch fett
    launchFett()

    # tear down
    endFett () 


""" This is the prepare function before launch (binaries, network,) """ 
@decorate.debugWrap
def prepareEnv ():
    printAndLog (f"Preparing the environment...")
    # cannot buildApps on aws
    if (isEnabled('buildApps') and isEqSetting('target','aws') and isEqSetting('mode','deploy')):
        warnAndLog (f"It is not allowed to <buildApps> on <AWS> in <deploy> mode. This will be switched off.")
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
            aws.setupKernelModules()
            aws.configTapAdaptor()
            aws.programAFI()
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
    xTarget.shutdown()


""" This is the teardown function """
@decorate.debugWrap
def endFett ():
    pass

""" This decides the classes hierarchy """
@decorate.debugWrap
def getClassType():
    if (isEqSetting('target','aws')):
        return getattr(aws,f"{getSetting('pvAWS')}Target")
    elif (isEqSetting('target','qemu')):
        return qemu.qemuTarget
    elif (isEqSetting('target','fpga')):
        gfeTestingScripts = getSettingDict('nixEnv',['gfeTestingScripts'])
        if (gfeTestingScripts not in os.environ):
            logAndExit (f"<${gfeTestingScripts}> not found in the nix path.",exitCode=EXIT.Environment)
        try:
            sys.path.append(os.environ[gfeTestingScripts])
            from test_gfe_unittest import TestLinux, TestFreeRTOS
        except Exception as exc:
            logAndExit (f"Failed to load <test_gfe_unittest> from <${gfeTestingScripts}>.",exc=exc,exitCode=EXIT.Environment)
        if (isEqSetting('xlen',32)):
            return type('classFpgaTarget',(fpga.fpgaTarget,TestFreeRTOS),dict())
        elif(isEqSetting('xlen',64)):
            return type('classFpgaTarget',(fpga.fpgaTarget,TestLinux),dict())
        else:
            logAndExit (f"Invalid <xlen={getSetting('xlen')}> value.",exitCode=EXIT.Dev_Bug)

    else:
        logAndExit (f"<launch.getClassType> is not implemented for <{getSetting('target')}>.",exitCode=EXIT.Dev_Bug)


