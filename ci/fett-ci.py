#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- Usage: `./fett-ci.py (--help | -h)`
"""

def exitFettCi (exitCode=-1,exc=None,message=None):
    if (message):
        print(f"(Error)~  FETT-CI: {message}")
    if (exc):
        print(f"(Error)~  <{exc.__class__.__name__}>: {exc}")
    if (exitCode == -1):
        print(f"(FATAL)~  End of FETT-CI: <JOB-FAILURE>")
    elif (exitCode == 0):
        print(f"(Info)~  End of FETT-CI: <JOB-SUCCESS>")
    else:
        print(f"(Info)~  End of FETT-CI: <JOB-FAILURE>")
    exit(exitCode)

def exitOnInterrupt (xSig,xFrame):
    signalNames = {2:'SIGINT', 15:'SIGTERM', 5:'SIGTRAP', 6:'SIGABRT'}
    if (xSig in signalNames):
        sigName = signalNames[xSig]
    else:
        sigName = f"signal#{xSig}"
    exitFettCi(message=f"Received <{sigName}>!")

try:
    import sys, os, glob
    import subprocess, argparse, signal
except Exception as exc:
    exitFettCi (exitCode=-1,exc=exc)

def main (xArgs):
    print(f"(Info)~  FETT-CI: Starting...")
    #important paths
    ciDir = os.path.abspath(os.path.dirname(__file__))
    repoDir = os.path.join(ciDir,os.pardir) 
    fettPyPath = os.path.join(repoDir,'fett.py')
    
    # Adjust optional arguments
    if (xArgs.jobTimeout):
        try:
            if ('h' in xArgs.jobTimeout):
                timeUnit = 'h'
                timeScale = 3600
            elif ('m' in xArgs.jobTimeout):
                timeUnit = 'm'
                timeScale = 60
            else:
                raise
            jobTimeout = timeScale*int(xArgs.jobTimeout.split(timeUnit)[0]) - 900 #leave 15 min for set up and storing artifacts
            if (jobTimeout <= 0):
                raise
        except Exception as exc:
            exitFettCi(message="Invalid timeout argument. Has to be in [\d+(hm)] format, and > 15m.",exc=exc)
    else:
        jobTimeout = None

    #nodes control
    nodeIndex = 0 if (not xArgs.nodeIndex) else xArgs.nodeIndex

    # Check runType
    if (xArgs.runType not in ['runPush', 'runDevPR', 'runPeriodic', 'runRelease']):
        exitFettCi(message="Invalid runType argument. Has to be in [runPush, runDevPR, runPeriodic, runRelease].")

    # Check number of configs + get the right config file
    if (xArgs.runType == 'runPush'): #Execute the files in ci/runOnPush
        dirConfigs = os.path.join(ciDir,'runOnPush')
        if (not os.path.isdir(dirConfigs)):
            exitFettCi(message=f"Directory <{dirConfigs}> cannot be accessed.")
        try:
            listConfigs = glob.glob(os.path.join(dirConfigs, '*.ini'))
        except Exception as exc:
            exitFettCi (message=f"Failed to list <{dirConfigs}/*.ini>.",exc=exc)
    else: #generate the config file
        # ------ Code here
        listConfigs = []

    # run the fett tool
    nErrs = 0 
    for xConfig in listConfigs:
        exitCode = 0 #success
        try:
            subprocess.run([fettPyPath,'-c',xConfig,'-d'], stdout=sys.stdout, stderr=sys.stderr, timeout=jobTimeout, check=True)
        except subprocess.CalledProcessError as exc:
            exitCode = exc.returncode
        except Exception as exc: #fatal
            exitFettCi (exitCode=-1,exc=exc)
        nErrs += int(exitCode != 0)

        # prepare artifacts
        # ------- Code here

    exitFettCi(exitCode=nErrs)


if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='FETT-CI (CI Entry to FETT-Target)')
    xArgParser.add_argument ('runType', help='The CI run type.')
    xArgParser.add_argument ('artifactSuffix', help='The suffix of the path to copy the artifacts to.')
    xArgParser.add_argument ('-i', '--nodeIndex', help='The node index within the job.')
    xArgParser.add_argument ('-N', '--nNodes', help='The total number of nodes.')
    xArgParser.add_argument ('-t', '--jobTimeout', help='The timeout (in hours) for executing fett.py. Before deducting 15 minutes.')
    xArgs = xArgParser.parse_args()

    #Trapping the signals
    signalsToCatch = [signal.SIGINT, signal.SIGTERM, signal.SIGTRAP, signal.SIGABRT]
    for xSignal in signalsToCatch:
        signal.signal(xSignal,exitOnInterrupt)

    main(xArgs)