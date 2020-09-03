""" EC2 Instance and Group Management

Convenience objects to access relevant fields from EC2 instances for CI type tasks. A
manager is created to create groups of instances where jobs can be dispatched.
"""
import re
import time

import boto3

from .aws_tools import *
from .logger import *


class InstanceManager:
    """ Manage EC2 Instances
    define group of EC2 instances, assign a workload and run
    """

    def __init__(self, cap=1, instances=None):
        if instances is None:
            instances = []

        self._cap = cap
        self._instances = instances
        self._running = []
        self._terminated = []
        self._results = []

        self._i = cap

    @log_assertion_fails
    def add_instance(self, instance):
        """append ec2 instance to instance manager"""
        assert isinstance(instance, Instance)
        log.debug(
            f"InstanceManager adding instance { instance.name } to { [x.name for x in self._instances] }"
        )
        self._instances.append(instance)
        return self

    def log_results(self, i):

        results_file_path = os.path.join("/tmp", i.id)
        try:
            # Read the log file in /tmp to get exit status
            with open(results_file_path, "r") as f:
                status = f.read().splitlines()[0]
        except Exception as exc:
            log.error(f"Failed to open file { results_file_path }", exc=exc)

        self._results.append([status, i.id, i.name])

        log.results(f"FINISHED: {i.name} ({i.id}), exited with status {status}.")

    @log_assertion_fails
    def run_all_instances(self, config=None):
        """run all jobs at the same time
        TODO: support running and terminating jobs non-uniformly
        """
        log.debug(
            f"Pool Run Instances started with instances { [[x.tags, x] for x in self._instances] } in capacity {self._cap}"
        )

        assert (len(self._instances)) > 0, "No instances were found."

        # Store the number of instanes to run for later use as
        #   self._instances is subject to change
        num_instances_total = len(self._instances)

        # Populate running_instances with $cap instances
        #   This uses the min of $cap and $(len(self._instances))
        running_instances = [
            self._instances.pop() for _ in range(min(self._cap, len(self._instances)))
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
            #   Therefore, we must check S3 to see if anything has happened
            #   We wait 5 s to keep polling down.
            time.sleep(5)
            s3 = poll_s3(config, [x.id for x in running_instances])

            # Check for finished ID
            if s3 != []:
                # We have found some instances that are done in S3
                # Generate a list that is a subset of running_instances containing only
                #   S3 terminated instances.
                finished_instances = [x for x in running_instances if x.id in s3]

                for i in finished_instances:
                    # Log results
                    self.log_results(i)

                    # If we have no more instances, remove from list, and do not replace
                    if len(self._instances) == 0:
                        terminate_instance(
                            i.id, dry_run=False, wait_for_termination=False
                        )
                        running_instances.remove(i)
                        log.debug(f"Removed instance { i.id } from _instances.")

                    # Else we replace it with the next item from _instances
                    else:
                        terminate_instance(
                            i.id, dry_run=False, wait_for_termination=True
                        )
                        replace_index = running_instances.index(i)
                        running_instances[replace_index] = self._instances.pop()

                        # Run new Instance
                        running_instances[replace_index].start()
                        log.info(
                            f"Replaced instance { i.id } with { running_instances[replace_index].id }"
                        )

                    # Print status to screen
                    to_run = len(self._instances)
                    running = len(running_instances)
                    finished = num_instances_total - (to_run + running)
                    percent_complete = int((finished / num_instances_total) * 100)
                    log.status(
                        f"Status: [ { to_run } / { running } / { finished } ] = { percent_complete }% ( To Run / Running / Finished )"
                    )

            time.sleep(2)

        # Print out the results from this run.
        log.status("Run Results:")
        failures = 0

        for result in self._results:
            if result[0] == "failure":
                log.info(f"Failure: Instance { result[2] } ({ result [1] })")
                failures += 1

        success_percentage = int(
            ((len(self._results) - failures) / len(self._results)) * 100
        )
        log.status(f"Overall: { success_percentage }% Success.")

    @property
    def instances(self):
        return self._instances


class Instance:
    """convenience wrapper class for boto3 EC2 Instance"""

    def __init__(
        self,
        ami,
        name="aws-test-suite",
        vpc_name="aws-controltower-VPC",
        security_group_name="FPGA Developer AMI-1-8-1-AutogenByAWSMP-1",
        instance_type="f1.2xlarge",
        key_name="nightly-testing",
        userdata=None,
        tags=None,
    ):

        if tags is None:
            tags = {}

        if not re.fullmatch("ami-[A-Za-z0-9]+", ami):
            ami = get_ami_id_from_name(ami)

        self._ami = ami
        self._name = name

        self._id = None

        self._vpc_name = vpc_name
        self._security_group_name = security_group_name
        self._instance_type = instance_type
        self._key_name = key_name
        self._userdata = userdata
        self._tags = tags
        self._tags["Name"] = self._name

        log.debug(
            f"Tags after name assignment in instance_manager.py is { self._tags } while name is { self._name }"
        )

    def start(self, **ec2_kwargs):
        """create boto3 ec2 instance"""
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
