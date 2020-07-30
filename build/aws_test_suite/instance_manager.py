import re

from .aws_tools import *


class InstanceManager:
    def __init__(self, cap=1, instances=None):
        if instances is None:
            instances = []

        self._cap = cap
        self._instances = instances

    def add_instance(self, ami, name):
        pass

    def terminate_instance(self, name):
        pass


class Instance:
    def __init__(self, ami, name, **kwargs):
        if not re.fullmatch('ami-[A-Za-z0-9]+', ami):
            ami = get_ami_id_from_name(ami)

        self._ami = ami
        self._name = name
