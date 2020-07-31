#! /usr/bin/env python3

# TODO: Add job to command added to userdata

# Import modules

import sys
import os

sys.path.insert(1, os.path.dirname(os.getcwd()))

import argparse
from datetime import datetime
from build.aws_test_suite import *

h = "[AWS Testing CI] : "


def main(args):
    console.log(f"{h}Welcome to the AWS testing app!")

    if args.init:
        a = AWSCredentials.from_interactive()
    elif args.credentials:
        a = AWSCredentials.from_credentials_file(args.credentials)
    else:
        try:
            a = AWSCredentials.from_credentials_file()
        except AssertionError:
            try:
                a = AWSCredentials.from_env_vars()
            except AssertionError:
                console.log(f"{h}Cannot get AWS credentials.", "Error")

    console.log(f"{h}Gathering run targets.")
    r = collect_run_names()

    i = InstanceManager(args.cap)

    console.log(f"{h}Creating userdata and instances.")

    count = args.count if 0 < args.count < len(r) else len(r)

    for j in range(args.run):
        for k in range(count):
            b = f"-{args.branch}" if args.branch else ""
            bb = f"-{args.binaries_branch}" if args.binaries_branch else ""
            jn = f"{args.name}-r{j}-i{k}{b}{bb}-{r[k]}"

            u = UserdataCreator.default(
                a, args.branch, args.binaries_branch, args.key_path
            )
            u.append(
                f"""runuser -l centos -c 'cd /home/centos/SSITH-FETT-Target && 
                           nix-shell --command "ci/fett-ci.py -ep AWSTesting runDevPR -job { jn } -i {str(k)}"' """
            )
            i.add_instance(
                Instance(args.ami, f"{args.name}-{str(k)}", userdata=u.userdata)
            )
            console.log(f"{h}Queueing {r[k]}.")

    console.log(f"{h}Starting instances and running tests.")
    while not i.done:
        i.start_instances().terminate_instances(True)

    console.log(f"{h}Tests done, and logs uploaded to S3.")
    console.log(f"{h}Exiting")
    exit(0)


if __name__ == "__main__":
    today = datetime.now().strftime("%m%d%y")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "ami", type=str, help="AWS AMI ID to use, i.e. 'ami-xxxxxxxxxxxxxxxxxx'"
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
        "--count",
        type=int,
        help="Number of possible configurations (same as length of the output of a dry run of the CI script).",
        default=-1,
    )
    parser.add_argument(
        "-cp",
        "--cap",
        type=int,
        help="The maximum number of instances running at once (default is 1)",
        default=1,
    )
    parser.add_argument(
        "-cd",
        "--credentials",
        type=str,
        help="AWS credentials file (Use either --init (-i) or --credentials (-cd))",
    )
    parser.add_argument(
        "-i",
        "--init",
        help="Initialize (first run or if tokens have expired) (Use either --init (-i) or --credentials (-cd))",
        action="store_true",
    )
    parser.add_argument(
        "-idx",
        "--instance-index",
        type=int,
        help="Specify a specific index of target to run - if entered, this program will run $RUNS worth of this "
        "instance index only.",
    )
    parser.add_argument(
        "-k",
        "--key-path",
        type=str,
        help='Path to the SSH key to be used with -b || -bb flags. Default: ["~/.ssh/aws-ci-gh"]',
        default="~/.ssh/aws-ci-gh",
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Base name to assign to instances created by this script (default is <current-date>-aws-testing)",
        default=f"{today}-aws-testing",
    )
    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        help="How many complete runs of all targets to make. Default 1.",
        default=1,
    )

    main(parser.parse_args())
