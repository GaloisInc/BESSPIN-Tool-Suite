#! /usr/bin/env python3
"""
--- fett-ci.py is the CI entry to the FETT-Target program. 
--- This files provides some utility functions
"""

from configs import *
import configparser, os, copy, time, glob, re
import traceback, shutil, subprocess, logging


def formatExc(exc):
    """ format the exception for printing """
    try:
        return f"<{exc.__class__.__name__}>: {exc}"
    except:
        return "<Non-recognized Exception>"


def printAndLog(message, doPrint=True):
    if doPrint:
        print("(Info)~  " + message)
    logging.info(message)


def warnAndLog(message, doPrint=True, exc=None):
    if doPrint:
        print("(Warning)~  " + message)
    logging.warning(message)
    if (exc):
        logging.warning(traceback.format_exc())

def errorAndLog(message, doPrint=True, exc=None):
    if doPrint:
        print("(Error)~  " + message)
    logging.error(message)
    if exc:
        logging.error(formatExc(exc))


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


def generateAllConfigs(baseRunType, flavor, runModes):
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
    for runMode in runModes:
        for xApp, xSet in appSets[baseRunType][flavor][runMode].items():
            inputSet = copy.deepcopy(xSet)
            inputDict = {"name": [xApp]}
            if (len(runModes)>1):
                inputDict["name"].append(runMode)
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
                if (xSetting not in ['runAllTests', 'randomizeParameters']): #repeated settings
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
    repoDir,
    configFile,
    artifactSuffix,
    entrypoint,
    exitCode,
    jobID,
    nodeIndex,
    targetLogs=True,
):
    # decide on the folder's name
    artifactsPath = os.path.splitext(os.path.basename(configFile))[0]
    if (entrypoint == 'OnPrem'): 
        artifactsPath += f"-{artifactSuffix}"

    if os.path.isdir(artifactsPath):  # already exists, add the date
        artifactsPath += f"-{int(time.time())}"

    # create the directory
    try:
        os.mkdir(artifactsPath)
    except Exception as exc:
        exitFettCi(message=f"Failed to create <{artifactsPath}>.", exc=exc)

    # This is assuming fett-ci uses the default workDir and targetLogFile
    # List all artifacts that generate a termination if they cannot be captured
    # This will run unless targetLogs=False, in which case we only add the non-
    #   essential logs.
    if targetLogs:
        workDir = os.path.join(repoDir, "workDir")
        targetLogFile = os.path.join(workDir, "fett.log")
        outFiles = glob.glob(os.path.join(workDir, "*.out"))

        listEssentialArtifacts = [configFile, targetLogFile] + outFiles

        # optional file
        makeOutPath = os.path.join(workDir, "build", "make.out")
        if (os.path.isfile(makeOutPath)):
            listEssentialArtifacts.append(makeOutPath)

    # List all artifacts that are fine to ignore if they do not exist.
    logFile = os.path.join(repoDir, "fett-ci.log")
    userDatatargetLogFile = os.path.join("/var", "log", "user-data.log")

    listArtifacts = [userDatatargetLogFile, logFile]

    # Collect the essential artifacts, exit fett-ci if it cannot be gotten.
    #   Only run this if we are collecting targetLogs
    if targetLogs:
        for xArtifact in listEssentialArtifacts:
            try:
                shutil.copy2(xArtifact, artifactsPath)
            except Exception as exc:
                exitFettCi(
                    message=f"Failed to copy <{xArtifact}> to <{artifactsPath}>.",
                    exc=exc,
                )
        #optional directories
        cweLogsPath = os.path.join(workDir,"cwesEvaluationLogs")
        if (os.path.isdir(cweLogsPath)):
            try:
                shutil.copytree(cweLogsPath, os.path.join(artifactsPath,"cwesEvaluationLogs"))
            except Exception as exc:
                exitFettCi(
                    message=f"Failed to copy <{cweLogsPath}> to <{artifactsPath}>.",
                    exc=exc,
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
                ciAWSbucket, exitFettCi, tarFileName, os.path.join('fett-target','ci','artifacts',jobID),
            )
        else:  # AWS Testing
            nonConfigJobId = jobID.split(f"-{artifactsPath}")[0]
            #Get the runIndex
            rIndexMatch = re.match(r"^.*-r(?P<rIndex>\d+)-i.*$",nonConfigJobId)
            if (rIndexMatch):
                rIndex = rIndexMatch.group('rIndex')
            else:
                warnAndLog(message="Failed to get the rIndex from the jobID. Using the timestamp instead.")
                rIndex = time.time()
            awsModule.uploadToS3(
                ciAWSbucketTesting, exitFettCi, tarFileName, os.path.join('artifacts',f"{nonConfigJobId}-r{rIndex}"),
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
            print(f"(Info)~  FETT-CI: Termination message sent to SQS.")
        else:  # AWS Testing
            instance_id = awsModule.getInstanceId(exitFettCi)
            resultFileName = os.path.join(repoDir, instance_id)
            with open(resultFileName, "w") as f:
                f.write(jobStatus)
                f.close()

            awsModule.uploadToS3(
                ciAWSbucketTesting, exitFettCi, resultFileName, f"communication/",
            )
            print(f"(Info)~  FETT-CI: Results uploaded to S3.")


def getFettTargetAMI (repoDir):
    """
    This functions tries to get the AMI using 4 different methods:
    1. (Recommended): Using boto3
    2. Using pygit2 since the tags contain an AMI ID
    3. Using `git tag` as a shell command
    4. Using the hardcoded value in `$repo/ci/configs.py`
    """

    # Main method
    try:
        import boto3
        ec2Client = boto3.client('ec2', region_name='us-west-2')
        allOwnerImages = ec2Client.describe_images(Owners=[backupFettAMI['OwnerId']])
        mostRecentAMI = backupFettAMI #Let's find newer AMIs
        for image in allOwnerImages['Images']:
            if (image['CreationDate'] > mostRecentAMI['CreationDate']):
                mostRecentAMI = image
        return mostRecentAMI['ImageId']
    except Exception as exc:
        warnAndLog (message="Failed to obtain the most recent AMI from AWS. Falling back to <pygit2>.",exc=exc)

    def getAMIfromRefs (listRefs, source):
        maxVersion = (0, None)
        for ref in listRefs:
            if (source == "pygit2"):
                if (not ref.startswith('refs/tags/v')):
                    continue
                xRef = ref.split('refs/tags/v')[1] #throw away the first part
            elif (source == "shell"):
                xRef = ref.split('v')[1]
            xItems = xRef.split('-')
            xVersion = xItems[0].split('.')
            valVersion = 1000*int(xVersion[0]) + int(xVersion[1]) # so "3.10" --> 3,010
            if (valVersion > maxVersion[0]):
                maxVersion = (valVersion, xItems)
        if (maxVersion[0]==0):
            raise Exception("getFettTargetAMI: Failed to find the newest version.")
        return '-'.join(maxVersion[1][1:])

    #Fall back to using "pygit2"
    try:
        from pygit2 import Repository
        repo = Repository(repoDir)
        return getAMIfromRefs (repo.listall_references(), "pygit2")
    except Exception as exc:
        warnAndLog (message="Failed to get the AMI using <pygit2>. Falling back to shell git.",exc=exc)

    #Fall back to parsing "git tag"
    try:
        allRefs = subprocess.getoutput(f"cd {repoDir} && git tag").splitlines()
        return getAMIfromRefs (allRefs, "shell")
    except Exception as exc:
        warnAndLog(message=f"Failed to get the AMI using <git tag> in shell. Falling back to the hardcoded backup value.", exc=exc)

    #Last resort: the hardcoded value
    try:
        return backupFettAMI['ImageId']
    except Exception as exc:
        warnAndLog(message=f"Failed to get the hardcoded AMI ID.", exc=exc)
        exitFettCi(message=f"Failed to find the AMI ID.")

