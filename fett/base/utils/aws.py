#! /usr/bin/env python3
"""
Functions required to use SQS and S3
NOTE: This module is shared between fett.py and fett-ci.py, so DO NOT IMPORT any functions
"""

def sendSQS (urlQueue, exitFunc, status, jobId, nodeId, reason='fett'):

    try:
        import boto3, json
    except Exception as exc:
        exitFunc(message=f"Failed to <import boto3, json>.",exc=exc)

    try:
        sqs = boto3.client('sqs')
    except Exception as exc:
        exitFunc(message=f"Failed to create the SQS object.",exc=exc)

    msg = json.dumps({
            "job": {
              "id": str(jobId),
              "status": status, 
              "reason": reason,
              "node": str(nodeId)
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