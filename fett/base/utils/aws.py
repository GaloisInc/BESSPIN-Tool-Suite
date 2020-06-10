#! /usr/bin/env python3
"""
Functions required to use SQS and S3
NOTE: This module is shared between fett.py and fett-ci.py, so DO NOT IMPORT any functions
"""

def sendSQS (urlQueue, exitFunc, status, jobId, nodeId, reason='fett', hostIp='None', fpgaIp='None'):

    try:
        import boto3, json, urllib.request
    except Exception as exc:
        exitFunc(message=f"Failed to <import boto3, json>.",exc=exc)

    try:
        sqs = boto3.client('sqs')
    except Exception as exc:
        exitFunc(message=f"Failed to create the SQS client.",exc=exc)

    # instanceID:
    try:
        instanceId = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read().decode()
    except Exception as exc:
        exitFunc(message=f"Failed to obtain the instance ID.",exc=exc)

    msg = json.dumps({
            "job": {
              "id": str(jobId),
              "status": status, 
              "reason": reason,
              "node": str(nodeId)
            },
            "instance": {
                "id": instanceId,
                "instance-ip": hostIp,
                "fpga-ip": fpgaIp
            }
        })

    try:
        sqs.send_message(
                QueueUrl=urlQueue,
                MessageBody=msg,
                DelaySeconds=0,
                MessageDeduplicationId=str(nodeId),
                MessageGroupId=str(jobId)
            )
    except Exception as exc:
        exitFunc(message=f"Failed to send the termination message to SQS.",exc=exc)

    return

def uploadToS3 (s3Bucket, exitFunc, tarball):
    try:
        import boto3, os
    except Exception as exc:
        exitFunc(message=f"Failed to <import boto3, os>.",exc=exc)

    try:
        s3 = boto3.client('s3')
    except Exception as exc:
        exitFunc(message=f"Failed to create the S3 client.",exc=exc)

    try:
        s3.upload_file(tarball, s3Bucket, os.path.basename(tarball))
    except Exception as exc:
        exitFunc(message=f"Failed to upload the tarball to the bucket.",exc=exc)


    