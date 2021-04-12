#! /usr/bin/env python3

"""
--- fetchProdLogs.py is a utility to fetch logs from BESSPIN production.
--- usage: fetchProdLogs.py [-h] [-g GREPFILTER] [-ts STARTTIME] [-tf ENDTIME]
                        [-o OUTPUTDIRECTORY] [-x] [-v]

Fetch BESSPIN logs from production

optional arguments:
  -h, --help            show this help message and exit
  -g GREPFILTER, --grepFilter GREPFILTER
                        Download the tarballs containing the search string.
  -ts STARTTIME, --startTime STARTTIME
                        Download the tarballs created after start time
                        (timestamp or yyyy-mm-dd).
  -tf ENDTIME, --endTime ENDTIME
                        Download the tarballs created before end time
                        (timestamp or yyyy-mm-dd).
  -o OUTPUTDIRECTORY, --outputDirectory OUTPUTDIRECTORY
                        Overwrites the default output directory:
                        $repoDir/logsDir/
  -x, --untar           Extracts all the tarballs after downloading.
  -v, --verbose         Prints the names of the files that are downloaded.
"""

import sys, os, traceback, shutil, signal, glob
import boto3, botocore, argparse, datetime, tarfile

prodBucket = 'master-ssith-besspin-researcher-artifacts'
artifactsPath = 'besspin/production/artifacts'

def formatExc (exc):
    """ format the exception for printing 
    
    ARGUMENTS:
    ----------
    exc: Exception
    
    RETURN:
    ------
    String: Either the text desription of the Exception, or 
                The <Non-recognized Exception> string.
    """
    try:
        return f"<{exc.__class__.__name__}>: {exc}"
    except:
        return '<Non-recognized Exception>'

def errorExit(message,exc=None):
    """
    Exits the utility and reports error

    ARGUMENTS:
    ----------
    message: String
        error message

    exc: Exception

    SIDE-EFFECTS:
    -------------
    - prints ERROR + error message + exception text if applicable
    - exits with code 1
    """
    if (exc):
        message += f"\n{formatExc(exc)}."
    print(f"(ERROR)~ {message}")
    # Uncomment for traceback.
    #if (exc):
    #    print(traceback.format_exc())
    exit(1)

def exitOnInterrupt (xSig,xFrame):
    """
    This function gets called if the utility catches a signal (2,5,6, or 15)

    ARGUMENTS:
    ----------
    xSig: Integer
        The caught signal number

    xFrame: Signal Object Frame
        Unused by the utility. Forced format by the signal package.

    SIDE-EFFECTS:
    -------------
    - Calls the errorExit function to exit with an error. 
    """
    signalNames = {2:'SIGINT', 15:'SIGTERM', 5:'SIGTRAP', 6:'SIGABRT'}
    if (xSig in signalNames):
        sigName = signalNames[xSig]
    else:
        sigName = f"signal#{xSig}"
    errorExit(f"Received <{sigName}>!")

def parseTimeInput (argDatetime):
    """
    Naive parsing for the input time string (utility argument)

    ARGUMENTS:
    --------
    argDatetime: Integer or String
        The input time: either timestamp (Integer) or yyyy-mm-dd (String)

    RETURN:
    -------
    datetime.datetime object with the chosen time
    """
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
            errorExit(f"<endTime={timeEnd}> should be after <startTime={timeStart}>.")

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
            if (xArgs.verbose):
                print(f"{filename}")
            try:
                s3.download_file(Bucket=prodBucket, Key=content['Key'], 
                            Filename=os.path.join(outDir,filename))
            except Exception as exc:
                errorExit("Failed to download!",exc=exc)

    # Extract the tarballs if instructed to do so
    if (xArgs.untar):
        for tarball in glob.glob(os.path.join(outDir,'*.tar.gz')):
            tarName = os.path.basename(tarball).split('.tar.gz')[0]
            try:
                xTar = tarfile.open(tarball)
                xTar.extractall(path=outDir)
                xTar.close()
                os.remove(tarball)
            except Exception as exc:
                errorExit(f"Failed to extract <{tarball}> to <{os.path.join(outDir,tarName)}>.",exc=exc) 

    
    print(f"\n{nFilesTot} available files.")
    textExtracted = 'and extracted in' if (xArgs.untar) else 'to'
    print(f"{nFilesDownloaded} tarballs downloaded {textExtracted} <{outDir}>.")


if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Fetch BESSPIN logs from production')
    xArgParser.add_argument ('-g', '--grepFilter', help='Download the tarballs containing the search string.')
    xArgParser.add_argument ('-ts', '--startTime', help='Download the tarballs created after start time (timestamp or yyyy-mm-dd).')
    xArgParser.add_argument ('-tf', '--endTime', help='Download the tarballs created before end time (timestamp or yyyy-mm-dd).')
    xArgParser.add_argument ('-o', '--outputDirectory', help='Overwrites the default output directory: $repoDir/logsDir/')
    xArgParser.add_argument ('-x', '--untar', help='Extracts all the tarballs after downloading.', action='store_true')
    xArgParser.add_argument ('-v', '--verbose', help='Prints the names of the files that are downloaded.', action='store_true')
    xArgs = xArgParser.parse_args()

    #Trapping the signals
    signalsToCatch = [signal.SIGINT, signal.SIGTERM, signal.SIGTRAP, signal.SIGABRT]
    for xSignal in signalsToCatch:
        signal.signal(xSignal,exitOnInterrupt)

    main(xArgs)