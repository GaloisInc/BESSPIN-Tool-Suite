#! /usr/bin/env python3

"""
--- fetchProdLogs.py is a utility to fetch logs from FETT production.
--- usage:
"""

import sys,os,traceback
import boto3

prodBucket = 'master-ssith-fett-target-researcher-artifacts'
artifactsPath = 'fett-target/production/artifacts'

def tryFunc (func,errorMessage,*args,**kwargs):
    try:
        return func(*args,**kwargs)
    except Exception as exc:
        errorExit(errorMessage,exc=exc)

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

def main():
    s3 = tryFunc(boto3.client,
                "Failed to create the S3 client.",
                's3',region_name='us-west-2')

    # fetch a list of all files
    listFiles = tryFunc(s3.list_objects_v2,
                    "Failed to list all files in artifacts path.",
                    Bucket=prodBucket, MaxKeys=10, Prefix=artifactsPath)


if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Fetch FETT logs from production')
    xArgParser.add_argument ('-g', '--grepFilter', help='Download the tarballs containing the search string.')
    xArgParser.add_argument ('-ts', '--startTime', help='Download the tarballs created after start time.')
    xArgParser.add_argument ('-tf', '--endTime', help='Download the tarballs created before end time.')
    xArgParser.add_argument ('-o', '--outputDirectory', help='Overwrites the default output directory: ./logsDir/')
    xArgs = xArgParser.parse_args()

    main(xArgs)