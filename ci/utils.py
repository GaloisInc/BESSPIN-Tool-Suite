#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- This files provides some utility functions
"""

from configs import *
import configparser, os, copy, time, glob, shutil, subprocess


def exitFettCi(exitCode=-1, exc=None, message=None):
    if message:
        print(f"(Error)~  FETT-CI: {message}")
    if exc:
        print(f"(Error)~  <{exc.__class__.__name__}>: {exc}")
    if exitCode == -1:
        print(f"(FATAL)~  End of FETT-CI: <JOB-FAILURE>")
    elif exitCode == 0:
        print(f"(Info)~  End of FETT-CI: <JOB-SUCCESS>")
    else:
        print(f"(Info)~  End of FETT-CI: <JOB-FAILURE>")
    exit(exitCode)


def exitOnInterrupt(xSig, xFrame):
    signalNames = {2: "SIGINT", 15: "SIGTERM", 5: "SIGTRAP", 6: "SIGABRT"}
    if xSig in signalNames:
        sigName = signalNames[xSig]
    else:
        sigName = f"signal#{xSig}"
    exitFettCi(message=f"Received <{sigName}>!")


def generateAllConfigs(baseRunType, flavor):
    # create a list of unique dictionaries. Each dictionary can become a .ini instance
    def createConfig(inputSet, inputDict):
        if not inputSet:  # we're done
            return

        newSetting = inputSet.pop()
        settingName = newSetting[0]
        values = list(newSetting[1])

        # Create a new set/dict for every extra value
        for iValue in values[1:]:
            newDict = copy.deepcopy(inputDict)
            allConfigs.append(newDict)
            newDict[settingName] = iValue
            newDict["name"] += [str(iValue)]
            newSet = copy.deepcopy(inputSet)
            createConfig(newSet, newDict)

        # Keep the inputDict for values[0]
        if len(values) > 1:
            inputDict["name"] += [str(values[0])]
        inputDict[settingName] = values[0]
        createConfig(inputSet, inputDict)

    allConfigs = []
    for xApp, xSet in appSets[baseRunType][flavor].items():
        inputSet = copy.deepcopy(xSet)
        inputDict = {"name": [xApp]}
        allConfigs.append(inputDict)
        createConfig(inputSet, inputDict)

    # Produce a consistent naming order:
    for xConfig in allConfigs:
        xConfig["name"] = "_".join(
            sorted(xConfig["name"])
        )  # sort the name components, then join them with '_'
    allConfigs.sort(
        key=lambda item: item["name"]
    )  # sort the list based on item['name']

    return allConfigs


def generateConfigFile(repoDir, outDir, dictConfig, testMode):
    # loading the template configuration file (the repo's default)
    templateConfigPath = os.path.join(repoDir, "config.ini")
    xConfig = configparser.ConfigParser()
    try:
        fConfig = open(templateConfigPath, "r")
        xConfig.read_file(fConfig)
        fConfig.close()
    except Exception as exc:
        exitFettCi(
            message=f"Failed to read configuration file <{templateConfigPath}>.",
            exc=exc,
        )

    # Adjusting the xConfig
    fileName = None
    for xSetting, xValue in dictConfig.items():
        wasSet = False
        if xSetting == "name":
            fileName = f"{xValue}.ini"
            continue
        for xSection in xConfig:
            if xSetting in xConfig[xSection]:
                xConfig.set(xSection, xSetting, str(xValue))
                wasSet = True
                break
        if not wasSet:
            exitFettCi(
                message=f"Failed to find the setting <{xSetting}> in <{templateConfigPath}>."
            )
    if not fileName:
        exitFettCi(message=f"Failed to find the key <name> in dictConfig.")

    # Creating the config file
    if testMode:
        dumpDir = os.path.join(outDir, "dumpIni")
        xConfigFilePath = os.path.join(dumpDir, fileName)
        print(f"\t{fileName}")
    else:
        xConfigFilePath = os.path.join(outDir, fileName)

    try:
        fConfig = open(xConfigFilePath, "w")
        xConfig.write(fConfig)
        fConfig.close()
    except Exception as exc:
        exitFettCi(
            message=f"Failed to write configuration file <{xConfigFilePath}>.", exc=exc
        )

    return xConfigFilePath


def prepareArtifact(
    repoDir, configFile, artifactSuffix, entrypoint, exitCode, jobID, nodeIndex
):
    # decide on the folder's name
    artifactsPath = (
        f"{os.path.splitext(os.path.basename(configFile))[0]}-{artifactSuffix}"
    )
    if os.path.isdir(artifactsPath):  # already exists, add the date
        artifactsPath += f"-{int(time.time())}"

    # create the directory
    try:
        os.mkdir(artifactsPath)
    except Exception as exc:
        exitFettCi(message=f"Failed to create <{artifactsPath}>.", exc=exc)

    # Move the important files there
    # This is assuming fett-ci uses the default workDir and logFile
    workDir = os.path.join(repoDir, "workDir")
    logFile = os.path.join(workDir, "fett.log")
    userDataLogFile = os.path.join("/var", "log", "user-data.log")
    outFiles = glob.glob(os.path.join(workDir, "*.out"))

    # List all artifacts that generate a termination if they cannot be captured
    listEssentialArtifacts = [configFile, logFile] + outFiles

    # List all artifacts that are fine to ignore if they do not exist.
    listArtifacts = [userDataLogFile]

    # Collect the essential artifacts, exit fett-ci if it cannot be gotten
    for xArtifact in listEssentialArtifacts:
        try:
            shutil.copy2(xArtifact, artifactsPath)
        except Exception as exc:
            exitFettCi(
                message=f"Failed to copy <{xArtifact}> to <{artifactsPath}>.", exc=exc
            )

    # Collect logs that will not generate termination if they cannot be found.
    for xArtifact in listArtifacts:
        try:
            subprocess.run(["sudo", "cp", xArtifact, artifactsPath])
            subprocess.run(
                [
                    "sudo",
                    "chown",
                    os.getlogin() + ":" + os.getlogin(),
                    os.join(artifactsPath, xArtifact),
                ]
            )
        except:
            print(f"(Warning)~  Unable to collect non-essential log file { xArtifact }")

    # Determine what to do with the dir of logs
    if entrypoint in ["AWS", "AWSTesting"]:
        # import the required modules
        try:
            import importlib.util, tarfile
        except Exception as exc:
            exitFettCi(message=f"Failed to <import importlib.util, tarfile>.", exc=exc)

        # Tar the artifact folder
        tarFileName = f"{artifactsPath}.tar.gz"
        try:
            xFile = tarfile.open(name=tarFileName, mode="w:gz")
            xFile.add(artifactsPath, arcname=None)
            xFile.close()
        except Exception as exc:
            exitFettCi(message=f"tar: error creating {tarFileName}", exc=exc)
        print(f"(Info)~  FETT-CI: Created <{tarFileName}> including all artifacts.")

        # import the shared module: aws.py
        moduleSpec = importlib.util.spec_from_file_location(
            "aws", os.path.join(repoDir, "fett", "base", "utils", "aws.py")
        )
        awsModule = importlib.util.module_from_spec(moduleSpec)
        moduleSpec.loader.exec_module(awsModule)

        # Upload the folder to S3
        if entrypoint == "AWS":
            awsModule.uploadToS3(
                ciAWSbucket,
                exitFettCi,
                tarFileName,
                f"fett-target/ci/artifacts/{jobID}/",
            )
        else:  # AWS Testing
            awsModule.uploadToS3(
                ciAWSbucketTesting, exitFettCi, tarFileName, f"aws-testing/{jobID}/",
            )
        print(f"(Info)~  FETT-CI: Artifacts tarball uploaded to S3.")

        # Send termination message to SQS
        jobStatus = "success" if (exitCode == 0) else "failure"
        if entrypoint == "AWS":
            awsModule.sendSQS(
                ciAWSqueue,
                exitFettCi,
                jobStatus,
                jobID,
                nodeIndex,
                reason="fett-target-ci-termination",
            )
        else:  # AWS Testing
            awsModule.sendSQS(
                ciAWSqueueTesting,
                exitFettCi,
                jobStatus,
                jobID,
                nodeIndex,
                reason="aws-testing-fett-target-ci-termination",
            )
        print(f"(Info)~  FETT-CI: Termination message sent to SQS.")
