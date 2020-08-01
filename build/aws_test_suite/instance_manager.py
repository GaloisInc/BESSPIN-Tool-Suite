import re

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

    def add_instance(self, instance):
        self._instances.append(instance)
        return self

    def start_instances(self, **ec2_kwargs):
        # assert self._capped, (
        #     "Maximum number of instances reached. call InstanceManager.terminate_instance first "
        #     "before starting another instance"
        # )

        start = len(self._terminated)
        end = (
            (self._cap + start)
            if self._cap + start < len(self._instances)
            else len(self._instances)
        )
        for i in range(start, end):
            if self._instances[i].id not in self._running:
                self._instances[i].start(**ec2_kwargs)
                self._running.append(self._instances[i].id)
        self._capped = True
        return self

    def terminate_instances(self, on_sqs=False):
        if on_sqs:
            wait_on_id_sqs(self._running)
            self._terminated.extend(self._running)
        else:
            for id in self._running:
                for instance in self._instances:
                    if id == instance.id:
                        instance.terminate()
                        self._terminated.append(id)
        self._running = []
        self._capped = False
        return self

    @property
    def instances(self):
        return self._instances

    @property
    def done(self):
        return len(self._instances) == len(self._terminated)


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
        self._id = launch_instance(
            self._ami,
            self._vpc_name,
            self._security_group_name,
            self._instance_type,
            self._key_name,
            self._userdata,
            self._tags,
            **ec2_kwargs
        )
        return self

    def terminate(self):
        assert self._id is not None, "Cannot terminate instance that has not started"
        terminate_instance(self._id)
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
    def instance(self):
        return self._instance

    @property
    def id(self):
        return self._id

    @userdata.setter
    def userdata(self, userdata):
        self._userdata = userdata
