### AWS TEST SUITE ###

# +-----------+
# |  Imports  |
# +-----------+
import json
import os
import shlex
import subprocess
import time
import boto3
import importlib.util

from .logger import *


def test_aws():
    """
    Tests the presence of the AWS CLI

    :return: A boolean for whether or not AWS CLI is installed
    :rtype: bool
    """

    try:
        subprocess_check_output("aws --version")
        return True
    except Exception as e:
        log.error(f"Test AWS: {e}")
        return False


# +-----------------------------+
# |  AWS Instance Manipulation  |
# +-----------------------------+


def subprocess_check_output(command=""):
    """
    Convenience to run command and return its output

    :param command: Shell command, defaults to ''
    :type command: str, optional

    :return: Standard output
    :rtype: str
    """

    proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    out = proc.stdout.read()
    return out


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
    ), f"No unique images found '{response['Images']}'"
    return response["Images"][0]["ImageId"]


def terminate_instance(instance_id, dry_run=True):
    """
    Terminate an instance by its instance id

    :param dry_run: Set to true, for safety
    :type dry_run: bool, optional
    """

    client = boto3.client("ec2")
    client.terminate_instances(InstanceIds=[instance_id], DryRun=dry_run)


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

    # TODO: handle launch_instance error case better
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


def collect_run_names():
    """
    Run fett-ci.py as a dryrun to generate a list of targets in their corresponding indexes to be run remotely

    :return: List of ini files to run
    :rtype: list
    """

    # Get path to the repoDir
    awsTestSuiteDir = os.path.abspath(os.path.dirname(__file__))
    buildDir = os.path.abspath(os.path.join(awsTestSuiteDir, os.pardir))
    repoDir = os.path.abspath(os.path.join(buildDir, os.pardir))

    log.debug(
        str(
            subprocess_check_output(
                str(os.path.join(repoDir, "ci", "fett-ci.py"))
                + " -X -ep AWS runDevPR -job 420"
            )
        )
    )
    unsorted = os.listdir("/tmp/dumpIni/")
    run_names = [run_name[:-4] for run_name in unsorted]

    log.info(f"Gathered Launch Targets:\t{run_names}")

    return run_names


# +-----------+
# |  AWS SQS  |
# +-----------+


def wait_on_id_sqs(ids):
    """
    Wait for an SQS message concerning all target in <ids> and terminate them, log results

    :param ids: List of instance ids started by AWS Tool Suite
    :type ids: list
    """

    log.info(f"Waiting for SQS Messages concerning ids { ids }")

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

    # Keep seeking messages until we have heard from all ids
    while len(ids) > 0:
        log.debug("Polling SQS")

        try:
            response = sqs.receive_message(
                QueueUrl=configs.ciAWSqueueTesting,
                VisibilityTimeout=5,  # 5 seconds are enough
                WaitTimeSeconds=20,  # Long-polling for messages, reduce number of empty receives
            )
        except:
            log.error(f"Failed to receive a response from the SQS queue.")

        if "Messages" in response:
            log.debug(f"Got SQS Response {response}")
            for message in response["Messages"]:
                body = json.loads(message["Body"])
                instance_id = body["instance"]["id"]
                log.info(
                    f'FINISHED: {body["instance"]["id"]}, exited with status {body["job"]["status"]}.'
                )
                log.debug(f"Comparing against {ids}")

                # If we have a message about an ID we have to terminate, terminate it, and remove the message.
                if instance_id in ids:
                    ids.remove(instance_id)
                    terminate_instance(instance_id, False)
                    log.info(f"Removed Instance {instance_id}")

                delete_message(message)

        time.sleep(2)
    time.sleep(120)
