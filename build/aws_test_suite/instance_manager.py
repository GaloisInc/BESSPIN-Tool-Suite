import re

from .aws_tools import *


class InstanceManager:
    def __init__(self, cap=1, instances=None):
        if instances is None:
            instances = []

        self._cap = cap
        self._instances = instances

    def add_instance(self, instance):
        self._instances.append(instance)

    def terminate_instance(self, name):
        pass


class Instance:
    def __init__(self, ami, name, **kwargs):
        if not re.fullmatch('ami-[A-Za-z0-9]+', ami):
            ami = get_ami_id_from_name(ami)

        self._ami = ami
        self._name = name

        self._handle_kwargs(kwargs)

    def _handle_kwargs(self, kwargs):
        self._vpc_name = kwargs['vpc_name'] if kwargs['vpc_name'] else 'aws-controltower-VPC'
        self._security_group_name = kwargs['security_group_name'] if kwargs['security_group_name'] else \
            'FPGA Developer AMI-1-8-1-AutogenByAWSMP-1'
        self._instance_type = kwargs['instance_type'] if kwargs['instance_type'] else 'f1.2xlarge'
        self._key_name = kwargs['key_name'] if kwargs['key_name'] else 'nightly-testing'
        self._userdata = kwargs['userdata'] if kwargs['userdata'] else None
        self._tags = kwargs['tags'] if kwargs['tags'] else {}
        self._tags['Name'] = self._name

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
