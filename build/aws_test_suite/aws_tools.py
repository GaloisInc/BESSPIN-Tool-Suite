### AWS TEST SUITE ###

# +-----------+
# |  Imports  |
# +-----------+
import json
import os
import boto3
import importlib.util

from .logger import *

# +-----------------+
# |  General Tools  |
# +-----------------+


@debug_wrap
def safe_traverse(in_dictionary, hierarchy):
    while hierarchy:
        item = hierarchy.pop(0)
        if item in in_dictionary:
            return safe_traverse(in_dictionary[item], hierarchy)
        else:
            log.error(
                f"safe_traverse: { item } not present in { in_dictionary }. Quitting."
            )
    return in_dictionary


# +-----------------------------+
# |  AWS Instance Manipulation  |
# +-----------------------------+
@debug_wrap
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

    images = safe_traverse(response, ["Images"])

    assert (
        len(images) == 1
    ), f"No unique images found '{images}' for ami name {ami_name}"
    return safe_traverse(images[0], ["ImageId"])


@debug_wrap
def terminate_instance(instance_id, dry_run=True, wait_for_termination=False):
    """
    Terminate an instance by its instance id

    dry_run sends a dry_run request, for testing purposes

    wait_for_termination will hold execution at this function until the instance
        has terminated.

    :param dry_run: Set to true, for safety
    :type dry_run: bool, optional

    :param wait_for_termination: Set to false
    :type wait_for_termination: bool, optional
    """

    log.debug(f"terminate_instances called with {locals()}")

    client = boto3.client("ec2")
    resp = client.terminate_instances(InstanceIds=[instance_id], DryRun=dry_run)
    log.info(f"Terminating instance: { instance_id }")
    log.debug(f"terminate_instances got response from terminate_instances() {resp}")

    # If wait_for_termination is passed, use boto3 waiter to wait for instance
    #   state to be terminated.
    if wait_for_termination:
        log.info(f"Waiting for instance { instance_id } to terminate.")
        log.debug(
            f"terminate_instances calling a waiter on termination status for { [instance_id] }"
        )

        waiter = client.get_waiter("instance_terminated")
        waiter.wait(InstanceIds=[instance_id])

        log.info(f"Instance { instance_id } Terminated.")


@debug_wrap
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
    response = client.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [security_group_name]}]
    )

    security_group = safe_traverse(
        safe_traverse(response, ["SecurityGroups"])[0], ["GroupId"]
    )

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
    except Exception as e:
        log.error(f"boto3.create_instances failed.", exc=exc)
        instance = None

    return instance[0].id


@debug_wrap
def poll_s3(config, instance_ids):
    """
    Poll AWS S3 for a file whose name is the instance id of any instance we are running.

    If found, read the termination status, log results, and then delete it.

    :return: instance id or None
    :rtype: str
    """

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
        s3 = boto3.client("s3")
    except Exception as exc:
        log.error(f"Failed to create the S3 client.", exc=exc)

    # Define a way to delete a message
    def delete_object(bucket_name, file_name):
        try:
            s3.delete_object(Bucket=bucket_name, Key=file_name)
            log.info(f"Succeeded in removing object { file_name } from { bucket_name }")
        except Exception as exc:
            log.warning(
                f"Failed to remove object { file_name } from { bucket_name }", exc=exc
            )

    log.debug("poll_s3 Polling S3")

    try:
        response = s3.list_objects_v2(
            Bucket=configs.ciAWSbucketTesting, Prefix="communication/"
        )
        log.debug(f"Polling S3 got response: { response }")

    except Exception as exc:
        log.error(
            f"Failed to recieve the contents of bucket { configs.ciAWSbucketTesting }.",
            exc=exc,
        )

    if "Contents" in response:
        contents = safe_traverse(response, ["Contents"])

        s3_finished_ids = [
            safe_traverse(obj, ["Key"]).split("communication/")[1] for obj in contents
        ]
        # Take the set intersection of the running ids and the completed ids in S3 to get
        #   Ids pertinant to this program.
        completed_ids = list(set(s3_finished_ids).intersection(set(instance_ids)))
        log.debug(
            f"Intersection of s3: { s3_finished_ids } and running: { instance_ids } is { completed_ids }"
        )

        if completed_ids:
            log.debug(
                f"Found S3 communications about running instances { completed_ids }"
            )

        # Download each result to /tmp, to be read later
        for instance_id in completed_ids:
            try:
                s3_file_name = "communication/" + instance_id
                results_file_path = os.path.join("/tmp", instance_id)
                s3.download_file(
                    Bucket=configs.ciAWSbucketTesting,
                    Key=s3_file_name,
                    Filename=results_file_path,
                )
                log.debug(f"Downloaded result for instance { instance_id } from S3")
                delete_object(configs.ciAWSbucketTesting, s3_file_name)
                log.debug(f"Deleted result for instance { instance_id } from S3")

            except Exception as exc:
                log.error(f"Failed to get file { instance_id } from AWS S3.", exc=exc)

        return completed_ids

    else:
        return []
