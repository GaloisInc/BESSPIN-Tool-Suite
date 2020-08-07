import re
import time
from .aws_tools import *
from .logger import *


class InstanceManager:
    def __init__(self, cap=1, instances=None):
        if instances is None:
            instances = []

        self._cap = cap
        self._instances = instances
        self._running = []
        self._terminated = []
        self._capped = False

        self._i = cap

    def add_instance(self, instance):
        self._instances.append(instance)
        return self

    def run_all_instances(self, config=None):
        log.debug(
            f"Pool Run Instances started with instances { [x.tags for x in self._instances] }in capacity {self._cap}"
        )

        running_instances = []

        assert (len(self._instances)) > 0, "No instances were found."

        # Populate running_instances with $cap instances
        #   This uses the min of $cap and $(len(self._instances))
        running_instances = [
            self._instances.pop() for x in range(min(self._cap, len(self._instances)))
        ]

        log.info(f"Populated running_instances with { len(running_instances) } items")

        # Start all those instances
        for i in running_instances:
            i.start()

        log.info(
            f"running_instances succeeded in starting instances: { [x.id for x in running_instances] }"
        )

        # Repeat while we still have instances left to add to running_instances
        #   or we still have running instances.
        while len(self._instances) > 0 or len(running_instances) > 0:
            # There are still instances left to run / running
            #   Therefore, we must check SQS to see if anything has happened
            sqs = poll_sqs(config)

            # Check for finished ID
            if sqs is not None:
                # Not an empty message - we have an ID
                for i in running_instances:
                    if i.id == sqs:
                        i.terminate()
                        log.info(f"Terminated instance { i.id }")

                        # If we have no more instances, remove from list, and do not replace
                        if len(self._instances) == 0:
                            running_instances.remove(i)
                            log.debug(f"Removed instance { i.id } _instances.")
                        # Else we replace it with the next item from _instances
                        else:
                            replace_index = running_instances.index(i)
                            running_instances[replace_index] = self._instances.pop()

                            # Wait 120 s to ensure spot has freed up.
                            time.sleep(120)

                            # Run new Instance
                            running_instances[replace_index].start()
                            log.info(
                                f"Replaced instance { i.id } with { running_instances[replace_index].id }"
                            )
            time.sleep(2)

    @property
    def instances(self):
        return self._instances


class Instance:
    def __init__(self, ami, name, **kwargs):
        if not re.fullmatch("ami-[A-Za-z0-9]+", ami):
            ami = get_ami_id_from_name(ami)

        self._ami = ami
        self._name = name

        self._id = None

        self._vpc_name = (
            kwargs["vpc_name"] if "vpc_name" in kwargs else "aws-controltower-VPC"
        )
        self._security_group_name = (
            kwargs["security_group_name"]
            if "security_group_name" in kwargs
            else "FPGA Developer AMI-1-8-1-AutogenByAWSMP-1"
        )
        self._instance_type = (
            kwargs["instance_type"] if "instance_type" in kwargs else "f1.2xlarge"
        )
        self._key_name = (
            kwargs["key_name"] if "key_name" in kwargs else "nightly-testing"
        )
        self._userdata = kwargs["userdata"] if "userdata" in kwargs else None
        self._tags = kwargs["tags"] if "tags" in kwargs else {}
        self._tags["Name"] = self._name

    def start(self, **ec2_kwargs):
        log.debug(f"Start() called on instance { self._tags }")
        self._id = launch_instance(
            self._ami,
            self._vpc_name,
            self._security_group_name,
            self._instance_type,
            self._key_name,
            self._userdata,
            self._tags,
            **ec2_kwargs,
        )
        log.debug(f"Start() finished with instance { self._id }")
        return self

    def terminate(self):
        assert self._id is not None, "Cannot terminate instance that has not started"
        terminate_instance(self._id, False)
        return self

    @property
    def ami(self):
        return self._ami

    @property
    def name(self):
        return self._name

    @property
    def vpc_name(self):
        return self._vpc_name

    @property
    def security_group_name(self):
        return self._security_group_name

    @property
    def instance_type(self):
        return self._instance_type

    @property
    def key_name(self):
        return self._key_name

    @property
    def userdata(self):
        return self._userdata

    @property
    def tags(self):
        return self._tags

    @property
    def id(self):
        return self._id

    @userdata.setter
    def userdata(self, userdata):
        self._userdata = userdata
