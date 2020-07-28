### AWS TEST SUITE ###

# +-----------+
# |  Imports  |
# +-----------+

import logging
import boto3

# +-----------------------------+
# |  AWS Instance Manipulation  |
# +-----------------------------+


def get_ami_id_from_name(ami_name):

    """
    from AMI name, get AMI ID
    allows the name to be passed to AWS management tools, rather than specifying the id
    """
    
    client = boto3.client("ec2")
    response = client.describe_images(Filters=[{"Name": "name", "Values": [ami_name]}])
    assert (
        len(response["Images"]) == 1
    ), f"No unique images found '{response['Images']}'"
    return response["Images"][0]["ImageId"]


def terminate_instance(instance_id, dry_run=True):
    
    """
    terminate an instance by its instance id
    :param dry_run: set to true, for safety
    """
    
    client = boto3.client("ec2")
    client.terminate_instances(InstanceIds=[instance_id], DryRun=dry_run)


def launch_instance(
    ami_name,
    vpc_name="aws-controltower-VPC",
    security_group_name="FPGA Developer AMI-1-8-1-AutogenByAWSMP-1",
    instance_type="f1.2xlarge",
    keyname="nightly-testing",
    user_data=None,
    tags={"Name": "cilib-default"},
    **ec2_kwargs,
):

    """
    create an ec2 instance

    convenience handling of boto3.create_instances -- allows the AMI, VPC and security to be referred to by name, rather
    than id. Also, defaults to values typically used during FETT development, only requiring the AMI name. Keyword
    arguments are passed directly to launch_instances call for extensibility.
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

    image_id = get_ami_id_from_name(ami_name)

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
        logging.error(f"boto3.create_instances failed with error '{e}'")
        instance = None

    return instance[0]

def collect_run_names():

	"""
	run fett-ci.py as a dryrun to generate a list of targets in their corresponding indexes to be run remotely
	"""

    logging.debug(str(subprocess_check_output("../../ci/fett-ci.py -X -ep AWS runDevPR -job 420")))
    unsorted = os.listdir("/tmp/dumpIni/")
    run_names = [run_name[:-4] for run_name in unsorted]
    run_names.sort()

    logging.info(
        f"Gathered Launch targets:\n{ run_names }"
    )

    return run_names

# +-----------+
# |  AWS SQS  |
# +-----------+

def wait_on_id_sqs(ids, name):

	"""
	Wait for an SQS message concerning all target in <ids> and terminate them, logging results
	"""

    # Start Boto3 Client
    try:
        sqs = boto3.client("sqs", region_name="us-west-2")
    except Exception as exc:
        logging.error(f"Failed to create the SQS client.")

    # Define a way to delete a message
    def delete_message(message):
        try:
            sqs.delete_message(
                QueueUrl=configs.ciAWSqueueNightly,
                ReceiptHandle=message["ReceiptHandle"],
            )
            logging.info(
                "Succeeded in removing message from SQS queue."
            )
        except Exception:
            logging.warning(
                "Failed to delete the message from the SQS queue."
            )

    # Keep seeking messages until we have heard from all ids
    while len(ids) > 0:
        try:
            response = sqs.receive_message(
                QueueUrl=configs.ciAWSqueueNightly,
                VisibilityTimeout=5,  # 5 seconds are enough
                WaitTimeSeconds=20,  # Long-polling for messages, reduce number of empty receives
            )
        except Exception:
            logging.error(f"Failed to receive a response from the SQS queue.")

        if "Messages" in response:
            logging.debug(f"Got SQS Response { response }")
            for message in response["Messages"]:
                body = json.loads(message["Body"])
                instance_id = body["instance"]["id"]
                logging.info(
                    f'FINISHED: { body["instance"]["id"] }, exited with status { body["job"]["status"] }.'
                )
                logging.debug(f'Comparing against { ids }')

                # If we have a message about an ID we have to terminate, terminate it, and remove the message.
                if instance_id in ids:
                    ids.remove(instance_id)
                    terminate_instance(
                        instance_id,
                        False
                    )
                    logging.info(f"Removed Instance { instance_id }")

                delete_message(message)

        time.sleep(2)

