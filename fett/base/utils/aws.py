#! /usr/bin/env python3
"""
Functions required to use SQS and S3
NOTE: This module is shared between fett.py and fett-ci.py, so DO NOT IMPORT any functions
"""

import logging, sys
from functools import wraps

def debugWrap (func):
    @wraps(func)
    def wrappedFn(*args, **kwargs):
        try:
            caller = sys._getframe(1).f_code.co_name
        except:
            caller = 'unknown-caller'
        logging.debug(f"Entering <{func.__name__}>. [called from <{caller}>]")
        #logging.debug(f">>>> args={args}, kwargs={kwargs}") #super-duper debug
        ret = func(*args, **kwargs)
        logging.debug(f"Exitting <{func.__name__}>.")
        return ret
    return wrappedFn


@debugWrap
def getInstanceId (exitFunc):
    try:
        import urllib.request
    except Exception as exc:
        exitFunc(message=f"Failed to <import urllib.request>.",exc=exc)

    try:
        return urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id').read().decode()
    except Exception as exc:
        exitFunc(message=f"Failed to obtain the instance ID.",exc=exc)

@debugWrap
def getInstanceIp (exitFunc):
    try:
        import urllib.request
    except Exception as exc:
        exitFunc(message=f"Failed to <import urllib.request>.",exc=exc)

    try:
        return urllib.request.urlopen('http://169.254.169.254/latest/meta-data/local-ipv4').read().decode()
    except Exception as exc:
        exitFunc(message=f"Failed to obtain the instance IP.",exc=exc)

@debugWrap
def sendSQS (urlQueue, exitFunc, status, jobId, nodeId, reason='fett', hostIp='None', fpgaIp='None'):
    logging.debug (f"sendSQS: args: status={status}, jobId={jobId}, nodeId={nodeId}," 
                    f" reason={reason}, hostIp={hostIp}, fpgaIp={fpgaIp}")
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

@debugWrap
def uploadToS3 (s3Bucket, exitFunc, tarball, pathInBucket):
    logging.debug (f"uploadToS3: args: tarball={tarball}, pathInBucket={pathInBucket}")
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

@debugWrap
def pollPortalQueueIndefinitely (urlQueue, exitFunc):
    try:
        import boto3, time
    except Exception as exc:
        exitFunc(message=f"Failed to <import boto3, time>.",exc=exc)

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
            logging.debug(f"pollPortalQueueIndefinitely: Message deleted!")
        except Exception as exc:
            exitFunc(message=f"Failed to delete the message from the SQS queue.",exc=exc)

    def formatExc (exc):
        """ format the exception for printing """
        try:
            return f"<{exc.__class__.__name__}>: {exc}"
        except:
            return '<Non-recognized Exception>'

    instanceId = getInstanceId(exitFunc)

    while (True):
        logging.debug("pollPortalQueueIndefinitely: polling...")
        try:
            response = sqs.receive_message(
                QueueUrl=urlQueue,
                MessageAttributeNames=[
                    'instance_id',
                ],
                VisibilityTimeout=3, # should be small not to hold each other's message
                WaitTimeSeconds=20 # Long-polling for messages, reduce number of empty receives
            )
        except Exception as exc:
            exitFunc(message=f"Failed to receive a response from the SQS queue.",exc=exc)

        if ('Messages' in response):
            for message in response['Messages']:
                try:
                    msgInstanceId = message['MessageAttributes']['instance_id']['StringValue']
                except Exception as exc:
                    logging.debug(f"pollPortalQueueIndefinitely: Failed to get msgInstanceId.\n{formatExc(exc)}.")
                    continue
                if (msgInstanceId == instanceId):
                    logging.debug(f"pollPortalQueueIndefinitely: Received message's instance ID matches!")
                    delete_message(message)
                    return

        time.sleep(60)            

