#! /usr/bin/env python3

"""
--- fetchProdLogs.py is a utility to fetch logs from FETT production.
--- usage:
"""

import sys,os,boto3

prodBucket = 'master-ssith-fett-target-researcher-artifacts'



def main():
    try:
        s3 = boto3.client('s3', region_name='us-west-2')
    except Exception as exc:
        exitFunc(message=f"Failed to create the S3 client.",exc=exc)




if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='Fetch FETT logs from production')
    xArgParser.add_argument ('-g', '--grepFilter', help='Download the tarballs containing the search string.')
    xArgParser.add_argument ('-ts', '--startTime', help='Download the tarballs created after start time.')
    xArgParser.add_argument ('-tf', '--endTime', help='Download the tarballs created before end time.')
    xArgParser.add_argument ('-o', '--outputDirectory', help='Overwrites the default output directory: ./logsDir/')
    xArgs = xArgParser.parse_args()

    main(xArgs)