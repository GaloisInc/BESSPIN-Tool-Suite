#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- usage: fett-ci.py [-h] (-art ARTIFACTSUFFIX | -job JOBID) [-i NODEINDEX]
                  [-N NNODES] [-t JOBTIMEOUT] [-X] -ep {OnPrem,AWS,AWSTesting}
                  [-m {fett,cwe,all}]
                  runType

FETT-CI (CI Entry to FETT-Target)

positional arguments:
  runType               The CI run type. [OnPrem: {runDevPR,runRelease,runOnPu
                        sh,runPeriodic}-{unix,freertos}, AWS: runDevPR]

optional arguments:
  -h, --help            show this help message and exit
  -art ARTIFACTSUFFIX, --artifactSuffix ARTIFACTSUFFIX
                        The suffix of the path to copy the artifacts to.
  -job JOBID, --jobID JOBID
                        The CI job ID.
  -i NODEINDEX, --nodeIndex NODEINDEX
                        The node index within the job.
  -N NNODES, --nNodes NNODES
                        The total number of nodes.
  -t JOBTIMEOUT, --jobTimeout JOBTIMEOUT
                        The timeout for executing fett.py. Before deducting 15
                        minutes.
  -X, --testOnly        This dumps all possible config permutations and some
                        meta data. Does not run anything.
  -ep {OnPrem,AWS,AWSTesting}, --entrypoint {OnPrem,AWS,AWSTesting}
                        Entrypoint: OnPrem | AWS | AWSTesting
  -m {fett,cwe,all}, --runMode {fett,cwe,all}
                        Run Mode: fett | cwe | all
"""

try:
    import sys, os, glob, shutil, time, itertools
    import json, configparser, socket, re, logging
    import subprocess, argparse, signal, copy
    from utils import *
    from pygit2 import Repository
except Exception as exc:
    exitFettCi(exitCode=-1, exc=exc)


def main(xArgs):
    print(f"(Info)~  FETT-CI: Starting on <{socket.gethostname()}>...")
    # important paths
    ciDir = os.path.abspath(os.path.dirname(__file__))
    repoDir = os.path.abspath(os.path.join(ciDir, os.pardir))
    fettPyPath = os.path.join(repoDir, "fett.py")

    # Set up Logging
    logFile = os.path.join(repoDir, "fett-ci.log")
    logLevel = logging.DEBUG
    logging.basicConfig(
        filename=logFile,
        filemode="w",
        format="%(asctime)s: (%(levelname)s)~  %(message)s",
        datefmt="%I:%M:%S %p",
        level=logLevel,
    )
    printAndLog(f"Fett CI Started")

    outDir = "/tmp"
    # Check runType
    baseRunTypes = ["runOnPush", "runDevPR", "runPeriodic", "runRelease"]
    if xArgs.entrypoint in ["AWS", "AWSTesting"]:
        if xArgs.runType not in baseRunTypes[1:2]:  # Only allow runDevPR on AWS for now
            exitFettCi(
                message=f"Invalid runType argument. For AWS, runType has to be in {baseRunTypes[1:2]}."
            )
        baseRunType = xArgs.runType
        flavor = "aws"
    elif xArgs.entrypoint == "OnPrem":
        flavors = ["unix", "freertos"]
        listRunTypes = [
            "-".join(pair) for pair in itertools.product(baseRunTypes, flavors)
        ]
        if xArgs.runType not in listRunTypes:
            exitFettCi(
                message=f"Invalid runType argument. For OnPrem, runType has to be in {listRunTypes}."
            )
        baseRunType, flavor = xArgs.runType.split("-")

    if xArgs.testOnly:
        printAndLog("FETT-CI: TestMode: Dumping some useful info...", doPrint=False)

    # nodes control
    if (not xArgs.nodeIndex):
        nodeIndex = 0
    elif xArgs.entrypoint == "OnPrem":
        nodeIndex = xArgs.nodeIndex - 1  # $CI_NODE_INDEX starts from 1
    else:
        nodeIndex = xArgs.nodeIndex

    # Check jobID is valid, if provided
    if xArgs.jobID:
        if not (re.match("^[A-Za-z0-9-_+.]+$", xArgs.jobID)):
            exitFettCi(
                message="Provided jobID contained invalid character(s). It must match regex '[A-Za-z0-9-_+.]'"
            )

    # Decide on artifact name -- There is no else as they are argparser grouped
    if xArgs.artifactSuffix:
        artifactSuffix = xArgs.artifactSuffix
    elif xArgs.jobID:
        artifactSuffix = f"{xArgs.jobID}-{nodeIndex}"

    # Check number of configs + get the right config file
    if baseRunType == "runOnPush":  # Execute the files in ci/runOnPush-flavor
        dirConfigs = os.path.join(ciDir, xArgs.runType)
        if not os.path.isdir(dirConfigs):
            exitFettCi(message=f"Directory <{dirConfigs}> cannot be accessed.")
        try:
            listConfigs = glob.glob(os.path.join(dirConfigs, "*.ini"))
        except Exception as exc:
            exitFettCi(message=f"Failed to list <{dirConfigs}/*.ini>.", exc=exc)

    # Else, generate the config file
    else:
        if (xArgs.runMode == 'all'):
            runModes = ['fett', 'cwe']
        else:
            runModes = [xArgs.runMode]
        allConfigs = generateAllConfigs(baseRunType, flavor, runModes)
        actualNumConfigs = len(allConfigs)
        if xArgs.testOnly:
            printAndLog(
                f"FETT-CI: <{xArgs.runType}> has <{actualNumConfigs}> configurations in total."
            )
            dumpDir = os.path.join(outDir, "dumpIni")
            printAndLog(
                f"FETT-CI: The configurations will be listed here and dumped in <{dumpDir}>:"
            )

            # If the dumpdir already exists, delete it
            if os.path.isdir(dumpDir):
                try:
                    shutil.rmtree(dumpDir)
                except Exception as exc:
                    exitFettCi(message=f"Failed to delete <{dumpDir}>.", exc=exc)

            # Create dumpdir
            try:
                os.mkdir(dumpDir)
            except Exception as exc:
                exitFettCi(message=f"Failed to create <{dumpDir}>.", exc=exc)

            # Generate configs
            for dictConfig in allConfigs:
                generateConfigFile(repoDir, outDir, dictConfig, xArgs.testOnly)

            if xArgs.entrypoint in ["AWS", "AWSTesting"]:  # generate the info file
                infoDict = {"nNodes": actualNumConfigs, "fettTargetAMI": getFettTargetAMI(repoDir)}
                infoFilePath = os.path.join(outDir, "awsCiInfo.json")
                try:
                    infoFile = open(infoFilePath, "w")
                    json.dump(infoDict, infoFile)
                    infoFile.close()
                except Exception as exc:
                    exitFettCi(message=f"Failed to generate <{infoFilePath}>.", exc=exc)
                printAndLog(
                    f"FETT-CI: Required info for AWS CI was generated into <{infoFilePath}>."
                )

        if (xArgs.nNodes) and (xArgs.nNodes != actualNumConfigs):
            exitFettCi(
                message=f"The actual number of configs <{actualNumConfigs}> does not match the total (={xArgs.nNodes}) declared in CI setup."
            )

        if (nodeIndex < 0) or (nodeIndex > actualNumConfigs - 1):
            exitFettCi(
                message=f"Invalid node index <{nodeIndex}> while the actual number of configs is <{actualNumConfigs}>."
            )

        configFilePath = generateConfigFile(
            repoDir, outDir, allConfigs[nodeIndex], False
        )
        listConfigs = [configFilePath]

    if xArgs.testOnly:
        printAndLog(f"List of .ini files to execute:\n { listConfigs }")
        warnAndLog("FETT-CI: This is not a real CI run.")
        exitFettCi(exitCode=0)

        # If we are in AWSTesting ep, we will check the git branches
    if xArgs.entrypoint == "AWSTesting":
        # Try to open the branches file, read the branches.
        try:
            with open(os.path.join(repoDir, "branches"), "r") as f:
                branches = f.read().splitlines()
                assert len(branches) == 2, "Failed to find 2 branches in branches file."
        except Exception as exc:
            # Prepare, upload to S3 and send SQS without TargetLogs, as nothing ran.
            errorAndLog(f"Error reading branches file.", exc=exc)
            prepareArtifact(
                repoDir,
                configFilePath,
                artifactSuffix,
                xArgs.entrypoint,
                -1,
                xArgs.jobID,
                nodeIndex,
                targetLogs=False,
            )
            exitFettCi(message="Error when trying to read branches from file.", exc=exc)

        try:
            targetRepo = Repository(repoDir)
            targetBranch = targetRepo.head.shorthand

            binariesRepo = Repository(os.path.join(repoDir, "SSITH-FETT-Binaries"))
            binariesBranch = binariesRepo.head.shorthand

            # Log
            printAndLog(
                f"Branch check: Target branch: is {targetBranch}, supposed to be {branches[0]}"
            )
            printAndLog(
                f"Branch check: Binaries branch: is {binariesBranch}, supposed to be {branches[1]}"
            )

            # Check branches
            if not branches[0] == "None":
                assert targetBranch == branches[0], "Failed branch check for Target."
            if not branches[1] == "None":
                assert binariesBranch == branches[1], "Failed branch check for Binaries"
                assert (
                    binariesRepo.status() == {}
                ), "Binaries Branch was not pulled successfully."

        except Exception as exc:
            # Prepare, upload to S3 and send SQS without TargetLogs, as nothing ran.
            errorAndLog(f"Wrong branches were checked out.", exc=exc)
            prepareArtifact(
                repoDir,
                configFilePath,
                artifactSuffix,
                xArgs.entrypoint,
                -1,
                xArgs.jobID,
                nodeIndex,
                targetLogs=False,
            )
            exitFettCi(message="Wrong branches were checked out.", exc=exc)

    # Adjust optional arguments
    if xArgs.jobTimeout:
        try:
            if "h" in xArgs.jobTimeout:
                timeUnit = "h"
                timeScale = 3600
            elif "m" in xArgs.jobTimeout:
                timeUnit = "m"
                timeScale = 60
            else:
                raise
            jobTimeout = (
                timeScale * int(xArgs.jobTimeout.split(timeUnit)[0]) - 900
            )  # leave 15 min for set up and storing artifacts
            if jobTimeout <= 0:
                raise
        except Exception as exc:
            exitFettCi(
                message="Invalid timeout argument. Has to be in [\d+(hm)] format, and > 15m.",
                exc=exc,
            )
    else:
        jobTimeout = None

    # Run the FETT Tool

    # Set the entrypoint to be same for AWSTesting and AWS for fett.py
    if xArgs.entrypoint == "AWSTesting":
        fettEntrypoint = "AWS"
    else:
        fettEntrypoint = xArgs.entrypoint

    nErrs = 0
    for xConfig in listConfigs:
        exitCode = 0  # success
        printAndLog(f"FETT-CI: Running <{os.path.basename(xConfig)}>.")
        sys.stdout.flush()
        try:
            subprocess.run(
                [fettPyPath, "-c", xConfig, "-ep", f"ci{fettEntrypoint}", "-d"],
                stdout=sys.stdout,
                stderr=sys.stderr,
                timeout=jobTimeout,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            exitCode = exc.returncode
        except Exception as exc:  # fatal
            exitFettCi(exitCode=-1, exc=exc)
        nErrs += int(exitCode != 0)

        # prepare artifacts
        prepareArtifact(
            repoDir,
            xConfig,
            artifactSuffix,
            xArgs.entrypoint,
            exitCode,
            xArgs.jobID,
            nodeIndex,
        )

    exitFettCi(exitCode=nErrs)


if __name__ == "__main__":
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser(
        description="FETT-CI (CI Entry to FETT-Target)"
    )
    xArgParser.add_argument(
        "runType",
        help="The CI run type. [OnPrem: {runDevPR,runRelease,runOnPush,runPeriodic}-{unix,freertos}, AWS: runDevPR]",
    )
    xGroupArtifacts = xArgParser.add_mutually_exclusive_group(required=True)
    xGroupArtifacts.add_argument(
        "-art",
        "--artifactSuffix",
        help="The suffix of the path to copy the artifacts to.",
    )
    xGroupArtifacts.add_argument("-job", "--jobID", help="The CI job ID.")
    xArgParser.add_argument(
        "-i", "--nodeIndex", help="The node index within the job.", type=int
    )
    xArgParser.add_argument(
        "-N", "--nNodes", help="The total number of nodes.", type=int
    )
    xArgParser.add_argument(
        "-t",
        "--jobTimeout",
        help="The timeout for executing fett.py. Before deducting 15 minutes.",
    )
    xArgParser.add_argument(
        "-X",
        "--testOnly",
        help="This dumps all possible config permutations and some meta data. Does not run anything.",
        action="store_true",
    )
    xArgParser.add_argument(
        "-ep",
        "--entrypoint",
        required=True,
        choices=["OnPrem", "AWS", "AWSTesting"],
        help="Entrypoint: OnPrem | AWS | AWSTesting",
    )
    xArgParser.add_argument(
        "-m",
        "--runMode",
        choices=["fett", "cwe", "all"],
        default="fett",
        help="Run Mode: fett | cwe | all",
    )
    xArgs = xArgParser.parse_args()

    # Trapping the signals
    signalsToCatch = [signal.SIGINT, signal.SIGTERM, signal.SIGTRAP, signal.SIGABRT]
    for xSignal in signalsToCatch:
        signal.signal(xSignal, exitOnInterrupt)

    main(xArgs)
