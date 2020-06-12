#! /usr/bin/env python3
"""
Functions required to use SQS and S3
NOTE: This module is shared between fett.py and fett-ci.py, so DO NOT IMPORT any functions
"""

def getInstanceId (exitFunc):
    try:
        import urllib.request
    except Exception as exc:
        exitFunc(message=f"Failed to <import urllib.request>.",exc=exc)

    try:
        return urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read().decode()
    except Exception as exc:
        exitFunc(message=f"Failed to obtain the instance ID.",exc=exc)


def sendSQS (urlQueue, exitFunc, status, jobId, nodeId, reason='fett', hostIp='None', fpgaIp='None'):

    try:
        import boto3, json
    except Exception as exc:
        exitFunc(message=f"Failed to <import boto3, json>.",exc=exc)

    try:
        sqs = boto3.client('sqs', region_name='us-west-2')
    except Exception as exc:
        exitFunc(message=f"Failed to create the SQS client.",exc=exc)

    # instanceID:
    instanceId = getInstanceId(exitFunc)

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
        exitFunc(message=f"Failed to send message to SQS.",exc=exc)

    return

def uploadToS3 (s3Bucket, exitFunc, tarball, pathInBucket):
    try:
        import boto3, os
    except Exception as exc:
        exitFunc(message=f"Failed to <import boto3, os>.",exc=exc)

    try:
        s3 = boto3.client('s3', region_name='us-west-2')
    except Exception as exc:
        exitFunc(message=f"Failed to create the S3 client.",exc=exc)

    try:
        s3.upload_file(tarball, s3Bucket, os.path.join(pathInBucket,os.path.basename(tarball)))
    except Exception as exc:
        exitFunc(message=f"Failed to upload the tarball to the bucket.",exc=exc)


def pollPortalQueueIndefinitely (urlQueue, exitFunc):
    try:
        import boto3
    except Exception as exc:
        exitFunc(message=f"Failed to <import boto3>.",exc=exc)

    try:
        sqs = boto3.client('sqs', region_name='us-west-2')
    except Exception as exc:
        exitFunc(message=f"Failed to create the SQS client.",exc=exc)

    def delete_message(message):
        try:
            sqs.delete_message(
                QueueUrl=urlQueue,
                ReceiptHandle=message['ReceiptHandle']
            )
        except Exception as exc:
            exitFunc(message=f"Failed to delete the message from the SQS queue.",exc=exc)

    instanceId = getInstanceId(exitFunc)

    wasReceived = False
    while (not wasReceived):
        try:
            response = sqs.receive_message(
                QueueUrl=urlQueue,
                MessageAttributeNames=[
                    'instance_id',
                ],
                VisibilityTimeout=60, # this is large enough
                WaitTimeSeconds=20 # Long-polling for messages, reduce number of empty receives
            )
        except Exception as exc:
            exitFunc(message=f"Failed to receive a response from the SQS queue.",exc=exc)

        if ('Messages' in response):
            for message in response['Messages']:
                try:
                    msgInstanceId = message['MessageAttributes']['instance_id']['StringValue']
                except:
                    continue
                if (msgInstanceId == instance_id):
                    delete_message(message)
                    wasReceived = True
                    break 

        time.sleep(60)            

    