### AWS TEST SUITE ###

# +-----------+
# |  Imports  |
# +-----------+
import json
import os
import boto3
import importlib.util
import random
import time

from .logger import *


# +-----------------------------+
# |  AWS Instance Manipulation  |
# +-----------------------------+
@log_assertion_fails
def get_ami_id_from_name(ami_name):
    """
    From AMI name, get AMI ID

    Allows the name to be passed to AWS management tools, rather than specifying the id

    :param ami_name: Name of the AMI instance
    :type ami_name: str

    :return: AMI ID
    :rtype: str
    """

    client = boto3.client("ec2")
    response = client.describe_images(Filters=[{"Name": "name", "Values": [ami_name]}])
    assert (
        len(response["Images"]) == 1
    ), f"No unique images found '{response['Images']}' for ami name {ami_name}"
    return response["Images"][0]["ImageId"]


def terminate_instance(instance_id, dry_run=True):
    """
    Terminate an instance by its instance id

    :param dry_run: Set to true, for safety
    :type dry_run: bool, optional
    """

    log.debug(f"terminate_instances called with {locals()}")

    client = boto3.client("ec2")
    resp = client.terminate_instances(InstanceIds=[instance_id], DryRun=dry_run)

    log.debug(f"terminate_instances got response from terminate_instances() {resp}")


def launch_instance(
    image_id,
    vpc_name="aws-controltower-VPC",
    security_group_name="FPGA Developer AMI-1-8-1-AutogenByAWSMP-1",
    instance_type="f1.2xlarge",
    keyname="nightly-testing",
    user_data=None,
    tags={"Name": "aws-test-suite-default"},
    **ec2_kwargs,
):
    """
    Creates an EC2 instance

    Convenience handling of boto3.create_instances -- allows the AMI, VPC and security to be referred to by name, rather
    than id. Also, defaults to values typically used during FETT development, only requiring the AMI name. Keyword
    arguments are passed directly to launch_instances call for extensibility.

    :param image_id: AMI ID
    :type image_id: str

    :param vpc_name: VPC name, defaults to 'aws-controltower-VPC'
    :type vpc_name: str

    :param security_group_name: Security group name, defaults to 'FPGA Developer AMI-1-8-1-AutogenByAWSMP-1'
    :type security_group_name: str

    :param instance_type: AMI instance type, defaults to 'f1.2xlarge'
    :type instance_type: str

    :param keyname: SSH key name, defaults to 'nightly-testing'
    :type keyname: str

    :param user_data: Script to be executed on the EC2 instance
    :type user_data: str

    :param tags: Other tags, such as instance name, defaults to {"Name": "aws-test-suite-default"}
    :type tags: dict

    :return: The instance object
    :rtype: dict
    """

    ec2 = boto3.resource("ec2")
    client = boto3.client("ec2")

    # get the VPC from ec2
    vpcfilter = [{"Name": "tag:Name", "Values": [vpc_name]}]
    vpc = list(ec2.vpcs.filter(Filters=vpcfilter))

    # get security group from ec2
    security_group = client.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [security_group_name]}]
    )["SecurityGroups"][0]["GroupId"]

    # get subnets and choose a public one
    subnets = list(
        vpc[0].subnets.filter(Filters=[{"Name": "tag:Name", "Values": ["*Public*"]}])
    )
    chosensubnet = subnets[0]

    try:
        # build out optional arguments
        optional_kwargs = ec2_kwargs
        if user_data:
            optional_kwargs["UserData"] = user_data
        if tags:
            optional_kwargs["TagSpecifications"] = (
                []
                if tags is None
                else [
                    {
                        "ResourceType": "instance",
                        "Tags": [{"Key": k, "Value": v} for k, v in tags.items()],
                    },
                ]
            )
        # create the instance
        instance = ec2.create_instances(
            ImageId=image_id,
            EbsOptimized=True,
            BlockDeviceMappings=([{"DeviceName": "/dev/sdb", "NoDevice": "",},]),
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            NetworkInterfaces=[
                {
                    "SubnetId": chosensubnet.subnet_id,
                    "DeviceIndex": 0,
                    "AssociatePublicIpAddress": True,
                    "Groups": [security_group],
                }
            ],
            KeyName=keyname,
            **optional_kwargs,
        )
    except client.exceptions.ClientError as e:
        log.error(f"boto3.create_instances failed with error '{e}'")
        instance = None

    return instance[0].id


# +-----------+
# |  AWS SQS  |
# +-----------+


def poll_sqs(config, instance_ids):
    """
    Get any new SQS messages that are in queue. Returns instance_id for a message.

    :return: instance id or None
    :rtype: str
    """

    log.debug(f"Beginning poll_sqs()")

    if config is not None:
        moduleSpec = importlib.util.spec_from_file_location("configs", config)
        configs = importlib.util.module_from_spec(moduleSpec)
        moduleSpec.loader.exec_module(configs)
    else:
        # Get path to the repoDir
        awsTestSuiteDir = os.path.abspath(os.path.dirname(__file__))
        buildDir = os.path.abspath(os.path.join(awsTestSuiteDir, os.pardir))
        repoDir = os.path.abspath(os.path.join(buildDir, os.pardir))

        # Import Configs from $repoDir/ci/configs.py
        moduleSpec = importlib.util.spec_from_file_location(
            "configs", os.path.join(repoDir, "ci", "configs.py")
        )
        configs = importlib.util.module_from_spec(moduleSpec)
        moduleSpec.loader.exec_module(configs)

    # Start Boto3 Client
    try:
        sqs = boto3.client("sqs", region_name="us-west-2")
    except:
        log.error(f"Failed to create the SQS client.")

    # Define a way to delete a message
    def delete_message(message):
        try:
            sqs.delete_message(
                QueueUrl=configs.ciAWSqueueTesting,
                ReceiptHandle=message["ReceiptHandle"],
            )
            log.info("Succeeded in removing message from SQS queue.")
        except:
            log.warning("Failed to delete the message from the SQS queue.")

    log.debug("poll_sqs Polling SQS")

    try:
        response = sqs.receive_message(
            QueueUrl=configs.ciAWSqueueTesting,
            VisibilityTimeout=5,  # 5 seconds are enough
            WaitTimeSeconds=20,  # Long-polling for messages, reduce number of empty receives
        )
    except:
        log.error(f"Failed to receive a response from the SQS queue.")

    if "Messages" in response:

        instance_ids_caught = []

        # Log the contents of the reponse
        log.debug(f"Got SQS Response {response}")
        for message in response["Messages"]:

            # Extract the body
            body = json.loads(message["Body"])
            instance_id = body["instance"]["id"]

            # Check if we have a SQS related to the instances we are looking for
            if instance_id in instance_ids:
                # Related
                log.results(
                    f'SQS Poll got SQS: FINISHED: {body["job"]["id"]}, exited with status {body["job"]["status"]}.'
                )
                delete_message(message)

                # Add the caught instance_id to the list
                instance_ids_caught.append(instance_id)

            else:
                # Unrelated
                log.debug(
                    f'SQS Poll got SQS: {instance_id} ({body["job"]["id"]}); status: {body["job"]["status"]}. Not in { instance_ids }'
                )
                # Wait a random amount of time to break cycles
                time.sleep(random.randint(3, 8))

        return instance_ids_caught

    # Nothing got, return None
    return None
