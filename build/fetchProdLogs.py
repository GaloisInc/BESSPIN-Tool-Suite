#! /usr/bin/env python3

"""
--- fetchProdLogs.py is a utility to fetch logs from FETT production.
--- usage:
"""

import sys, os, traceback, shutil, signal
import boto3, botocore, argparse, datetime

prodBucket = 'master-ssith-fett-target-researcher-artifacts'
artifactsPath = 'fett-target/production/artifacts'

def formatExc (exc):
    """ format the exception for printing """
    try:
        return f"<{exc.__class__.__name__}>: {exc}"
    except:
        return '<Non-recognized Exception>'

def errorExit(message,exc=None):
    if (exc):
        message += f"\n{formatExc(exc)}."
    print(f"(ERROR)~ {message}")
    # Uncomment for traceback.
    #if (exc):
    #    print(traceback.format_exc())
    exit(1)

def exitOnInterrupt (xSig,xFrame):
    signalNames = {2:'SIGINT', 15:'SIGTERM', 5:'SIGTRAP', 6:'SIGABRT'}
    if (xSig in signalNames):
        sigName = signalNames[xSig]
    else:
        sigName = f"signal#{xSig}"
    errorExit(f"Received <{sigName}>!")

def parseTimeInput (argDatetime):
    def parseTimestamp(timestamp):
        try:
            return datetime.datetime.fromtimestamp(timestamp).replace(tzinfo=datetime.timezone.utc)
        except Exception as exc:
            errorExit(f"Invalid input timestamp <{timestamp}>.",exc=exc)
    
    def parseDate(date):
        try:
            return datetime.datetime(*[int(elem) for elem in date.split('-')], tzinfo=datetime.timezone.utc)
        except Exception as exc:
            errorExit(f"Invalid input date <{date}>. Please use the format <yyyy-mm-dd>.",exc=exc)

    try:
        timestamp = int(argDatetime)
    except:
        return parseDate(argDatetime)
    
    return parseTimestamp(timestamp)

def main(xArgs):

    try:
        s3 = boto3.client('s3',region_name='us-west-2')
    except Exception as exc:
        errorExit("Failed to create the S3 client.",exc=exc)

    #Check credentials
    try:
        s3.head_bucket(Bucket=prodBucket)
    except Exception as exc:
        errorExit("Failed to verify AWS credentials.",exc=exc)

    # check the output directory
    buildDir = os.path.abspath(os.path.dirname(__file__))
    repoDir = os.path.abspath(os.path.join(buildDir,os.pardir))
    if (xArgs.outputDirectory):
        outDir = os.path.abspath(xArgs.outputDirectory)
    else:
        outDir = os.path.join(repoDir,'logsDir')
    if (os.path.isdir(outDir)): # already exists, delete
        try:
            shutil.rmtree(outDir)
        except Exception as exc:
            errorExit(f"Failed to delete the existing <{outDir}>.",exc=exc)
    try:
        os.mkdir(outDir)
    except Exception as exc:
        errorExit(f"Failed to create the output directory <{outDir}>.",exc=exc)

    print(f"Downloading files to <{outDir}>.")

    # Check that the input times are valid
    if (xArgs.startTime or xArgs.endTime):
        doCheckTime = True
        if (xArgs.startTime): # check starting time
            timeStart = parseTimeInput(xArgs.startTime)
        else:
            timeStart = datetime.datetime(2020, 7, 14, tzinfo=datetime.timezone.utc) #before launch date
        if (xArgs.endTime): # check ending time
            timeEnd = parseTimeInput(xArgs.endTime)
        else:
            timeEnd = datetime.datetime(2100, 1, 1, tzinfo=datetime.timezone.utc) #We're all be dead by then

        if (timeEnd < timeStart):
            errorExit(f"<endTime={timeEnd}> should be after <startTime={timeStart}>.",exc=exc)

        print(f"Downloading files modified between <{timeStart}> and <{timeEnd}>.")

    else:
        doCheckTime = False

    # Be more verbose
    if (xArgs.grepFilter):
        print(f"Downloading files containing <{xArgs.grepFilter}> in their name.")
                
    # Get a paginator (instead of looping using termination tokens ourselves in case >1000 files)
    try:
        paginator = s3.get_paginator('list_objects_v2')
    except Exception as exc:
        errorExit("Failed to obtain the list_objects_v2 paginator.",exc=exc)

    # Use the paginator to fetch pages containing the list of all files
    try:
        pages = paginator.paginate(Bucket=prodBucket, MaxKeys=1000, Prefix=artifactsPath) #1000 is the max anyway
    except Exception as exc:
        errorExit("Failed to obtain the list of all files using paginate",exc=exc)

    # loop through the files to select and download
    nFilesTot = 0
    nFilesDownloaded = 0
    for page in pages:
        nFilesTot += len(page['Contents'])
        for content in page['Contents']:
            filename = os.path.basename(content['Key'])

            # Check if this file should be selected
            # ----Check the grep filter
            if (xArgs.grepFilter):
                if (xArgs.grepFilter not in filename):
                    continue #skip this file

            # ---- Check the start and end time
            if (doCheckTime):
                # get the time of the file itself
                timeFile = content['LastModified']
                if ((timeFile<timeStart) or (timeFile>timeEnd)):
                    continue #skip this file
            
            # Download the file
            nFilesDownloaded += 1
            if (xArgs.Verbose):
                print(f"{filename}")
            try:
                s3.download_file(Bucket=prodBucket, Key=content['Key'], 
                            Filename=os.path.join(outDir,filename))
            except Exception as exc:
                errorExit("Failed to download!",exc=exc)

    print(f"\n{nFilesTot} available files.")
    print(f"{nFilesDownloaded} downloaded to <{outDir}>.")

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Fetch FETT logs from production')
    xArgParser.add_argument ('-g', '--grepFilter', help='Download the tarballs containing the search string.')
    xArgParser.add_argument ('-ts', '--startTime', help='Download the tarballs created after start time (timestamp or yyyy-mm-dd).')
    xArgParser.add_argument ('-tf', '--endTime', help='Download the tarballs created before end time (timestamp or yyyy-mm-dd).')
    xArgParser.add_argument ('-o', '--outputDirectory', help='Overwrites the default output directory: $repoDir/logsDir/')
    xArgParser.add_argument ('-v', '--Verbose', help='Prints the names of the files that are downloaded.', action='store_true')
    xArgs = xArgParser.parse_args()

    #Trapping the signals
    signalsToCatch = [signal.SIGINT, signal.SIGTERM, signal.SIGTRAP, signal.SIGABRT]
    for xSignal in signalsToCatch:
        signal.signal(xSignal,exitOnInterrupt)

    main(xArgs)