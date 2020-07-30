#! /usr/bin/env python3

import argparse
from datetime import datetime
from build import aws_test_suite as ats


def main(args):
    ats.print('Welcome to the nightly testing app!')

    if args.init:
        a = ats.AWSCredentials.from_interactive()
    elif args.credentials:
        a = ats.AWSCredentials.from_credentials_file(args.credentials)
    else:
        try:
            a = ats.AWSCredentials.from_credentials_file()
        except AssertionError:
            try:
                a = ats.AWSCredentials.from_env_vars()
            except AssertionError:
                ats.print('Cannot get AWS credentials', 'Error')

    e = ats.EC2WorkGroup(args.cap)  # TODO: do something??


if __name__ == "__main__":
    today = datetime.now().strftime("%m%d%y")

    parser = argparse.ArgumentParser()
    # parser.add_argument("ami", type=str, help="AWS AMI ID to use, i.e. 'ami-xxxxxxxxxxxxxxxxxx'")
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
        default=8,
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
        help="AWS credentials file (Use either --init (-i) or --credentials (-cd))"
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
        help="Base name to assign to instances created by this script (default is <current-date>-nightly)",
        default=f"{today}-nightly",
    )
    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        help="How many complete runs of all targets to make. Default 1.",
        default=1,
    )

    main(parser.parse_args())
