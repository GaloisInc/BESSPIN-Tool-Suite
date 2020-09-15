#! /usr/bin/env python3

# Import modules
import sys, os, time

sys.path.insert(1, os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from build.aws_test_suite import *

import argparse, subprocess, shlex, json, hashlib
from datetime import datetime


h = "[AWS Testing CI] : "


def get_ami_from_ci_json():
    """
    Get the ami from /tmp/awsCiInfo.json
    """

    try:
        with open("/tmp/awsCiInfo.json", "r") as f:
            aws_ci_info = json.load(f)
        return aws_ci_info["fettTargetAMI"]
    except Exception as exc:
        log.error("Failed to get Fett AMI from /tmp/awsCiInfo.json.", exc=exc)


def collect_run_names(repoDir, runMode):
    """
    Run fett-ci.py as a dryrun to generate a list of targets in their corresponding indexes to be run remotely

    :return: List of ini files to run
    :rtype: list
    """

    log.debug(
        str(
            subprocess.check_output(
                shlex.split(
                    str(os.path.join(repoDir, "ci", "fett-ci.py"))
                    + f" -X -ep AWS runDevPR -job 420 -m {runMode}"
                )
            )
        )
    )
    unsorted = os.listdir("/tmp/dumpIni/")
    # Restore the order these are in when printed.
    unsorted.sort()
    run_names = [run_name[:-4] for run_name in unsorted]

    log.info(f"Gathered Launch Targets:{run_names}")

    return run_names


def main(args):

    # Find repo dir
    # Get path to the repoDir
    ciDir = os.path.abspath(os.path.dirname(__file__))
    repoDir = os.path.abspath(os.path.join(ciDir, os.pardir))

    log.info(f"{h}Welcome to the AWS testing app!")

    # log arguments to main()
    log.debug(f"aws-testing-ci.py started with arguments { args }")

    # Check in envs, otherwise error
    a = AWSCredentials.from_env_vars()

    # Make sure that the region and format are written in ~/.aws/config
    AWSConfig.check_write_aws_config()

    log.info(f"{h}AWSCredentials gathered!")

    # Get list of all targets for fett-ci.py
    log.info(f"{h}Gathering run targets.")
    r = collect_run_names(repoDir, args.runMode)

    # Check the pem_key_name argument to make sure the user did
    #   not input the .pem extension
    pem_key_name = args.pem_key_name

    if pem_key_name.endswith(".pem"):
        pem_key_name = pem_key_name.split(".pem")[0]

    # Start an instance manager
    i = InstanceManager(args.cap)

    log.info(f"{h}Creating userdata and instances.")

    # Generate a list of indices to be tested on each run
    if args.instance_indices:
        indices_to_run = args.instance_indices
    else:
        indices_to_run = list(range(len(r)))

    # Get the AMI, either from args, or by using getFettTargetAMI()
    if args.ami:
        ami = args.ami
    else:
        ami = get_ami_from_ci_json()
        log.debug(
            f"AMI Parameter was not specified, got { ami } from /tmp/awsCiInfo.json/"
        )

    log.debug(f"Indices to run { indices_to_run }")

    log.info(
        f"Queueing { len(indices_to_run)*args.runs } instances ({ args.runs } runs)..."
    )

    # Determine branches for the job and instance name string
    b = f"-{args.branch}" if args.branch else ""
    bb = f"-{args.binaries_branch}" if args.binaries_branch else ""
    try:
        jobID = hashlib.md5(bytes(f'{args.name}{b}{bb}-{time.time()}','utf-8')).hexdigest()
        log.info(f"The run's ID is <{jobID}>.")
    except Exception as exc:
        log.error("Failed to get the hash of the run.", exc=exc)

    # Repeat number of runs
    for j in range(args.runs):

        # Repeat for targets
        for k in indices_to_run:
            # Build instance name string
            #   Need to replace '/' with '_' so that when S3 files are created, it does not
            #   Think it needs a new directory.
            n = f"{args.name}-r{j}-i{k}-{r[k]}-{jobID}".replace("/", "_")
            log.debug(f"Name String: { n }")

            # Compose userdata based on args
            u = UserdataCreator.default(
                a, n, k, args.branch, args.binaries_branch, args.key_path, args.runMode
            )

            # Add this instance to InstanceManager
            i.add_instance(
                Instance(ami, f"{n}", userdata=u.userdata, key_name=pem_key_name)
            )
            log.debug(f"{h}Queueing {r[k]}, with name {n}.")

    log.info(f"{h}Queued all instances. Starting and testing instances")

    # Run all instances according to the capacity specified.
    i.run_all_instances()

    log.info(f"{h}Tests done, and logs uploaded to S3.")
    log.info(f"{h}Exiting...")
    exit(0)


if __name__ == "__main__":

    today = datetime.now().strftime("%m%d%y")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a",
        "--ami",
        type=str,
        help="AWS AMI ID to use, i.e. 'ami-xxxxxxxxxxxxxxxxxx'. If left empty, defaults to the most recent tagged AMI in SSITH-FETT-Target.",
    )
    parser.add_argument(
        "-b",
        "--branch",
        type=str,
        help="The branch of FETT-Target to check out on the AWS instance, and run tests on. Defaults to whatever is "
        "present on AMI",
    )
    parser.add_argument(
        "-bb",
        "--binaries-branch",
        type=str,
        help="The branch of FETT-Bineries to check out on the AWS instance, and run tests on. Defaults to whatever is "
        "present on AMI",
    )
    parser.add_argument(
        "-c",
        "--cap",
        type=int,
        help="The maximum number of instances running at once (default is 1)",
        default=1,
    )
    parser.add_argument(
        "-i",
        "--instance-indices",
        type=int,
        nargs="*",
        help="Specify a list of indices of target(s) to run - if entered, this program will run $RUNS worth of this set "
        "of instance indices only. Enter separated by spaces.",
    )
    parser.add_argument(
        "-k",
        "--key-path",
        type=str,
        help='Path to the SSH key to be used with -b || -bb flags. Default: ["~/.ssh/id_rsa"]',
        default="~/.ssh/id_rsa",
    )
    parser.add_argument(
        "-p",
        "--pem-key-name",
        type=str,
        help="Name of the *.pem key to use in AWS when creating the instance. Defaults to nightly-testing",
        default="nightly-testing",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Base name to assign to instances created by this script (default is <current-date>-aws-testing)",
        default=f"{today}-aws-test-suite",
    )
    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        help="How many complete runs of all targets to make. Default 1.",
        default=1,
    )
    parser.add_argument(
        "-m",
        "--runMode",
        choices=["fett", "cwe", "all"],
        default="fett",
        help="Run Mode: fett | cwe | all",
    )

    main(parser.parse_args())
