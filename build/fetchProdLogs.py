#! /usr/bin/env python3

"""
--- fetchProdLogs.py is a utility to fetch logs from FETT production.
--- usage:
"""

import sys, os, traceback, shutil, signal
import boto3, botocore, argparse

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
    if (exc):
        print(traceback.format_exc())
    exit(1)

def exitOnInterrupt (xSig,xFrame):
    signalNames = {2:'SIGINT', 15:'SIGTERM', 5:'SIGTRAP', 6:'SIGABRT'}
    if (xSig in signalNames):
        sigName = signalNames[xSig]
    else:
        sigName = f"signal#{xSig}"
    errorExit(f"Received <{sigName}>!")

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
            if (xArgs.grepFilter):
                if (xArgs.grepFilter not in filename):
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
    xArgParser.add_argument ('-ts', '--startTime', help='Download the tarballs created after start time.')
    xArgParser.add_argument ('-tf', '--endTime', help='Download the tarballs created before end time.')
    xArgParser.add_argument ('-o', '--outputDirectory', help='Overwrites the default output directory: $repoDir/logsDir/')
    xArgParser.add_argument ('-v', '--Verbose', help='Prints the names of the files that are downloaded.', action='store_true')
    xArgs = xArgParser.parse_args()

    #Trapping the signals
    signalsToCatch = [signal.SIGINT, signal.SIGTERM, signal.SIGTRAP, signal.SIGABRT]
    for xSignal in signalsToCatch:
        signal.signal(xSignal,exitOnInterrupt)

    main(xArgs)