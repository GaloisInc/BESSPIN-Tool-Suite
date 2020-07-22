#! /usr/bin/env python3

import subprocess, json, os, argparse, math, time, boto3, importlib, json
from pathlib import Path
from datetime import datetime

import configs

run_names = []

# import the shared module: aws.py
moduleSpec = importlib.util.spec_from_file_location(
    "aws", os.path.join("../", "fett", "base", "utils", "aws.py")
)
awsModule = importlib.util.module_from_spec(moduleSpec)
moduleSpec.loader.exec_module(awsModule)

## TODO
#  - Add `source ~/.zshrc` robustness
#  - General neatness
#  - Robustness to exceeding vCPU capacity
#  - Ability to run multiple identical tests at the same time and get SQS results.


def print_and_exit(message=""):
    print(f"{ message }\n(Error)~ Exiting nightly testing.")
    exit(0)


def subprocess_call(command):
    return subprocess.call(command.split(sep=" "))


def subprocess_check_output(command):
    proc = subprocess.Popen(command.split(sep=" "), stdout=subprocess.PIPE)
    out = proc.stdout.read()
    return out


def append_to_userdata(command_list):
    with open(Path().absolute() / "userdata.txt", "a") as f:
        f.write("\n".join(command_list))
        f.write("\n")


def collect_run_names():
    global run_names

    subprocess_call("./fett-ci.py -X -ep AWS runDevPR -job 420")
    run_names = [run_name[:-4] for run_name in os.listdir("/tmp/dumpIni/")]
    run_names.sort()

    print(f"(Info)~ Collected run names { run_names }")


def wait_on_ids_sqs(ids, name):

    # Start Boto3 Client
    try:
        sqs = boto3.client("sqs", region_name="us-west-2")
    except Exception as exc:
        print(f"Failed to create the SQS client.")

    # Define a way to delete a message
    def delete_message(message):
        try:
            sqs.delete_message(
                QueueUrl=configs.ciAWSqueueNightly,
                ReceiptHandle=message["ReceiptHandle"],
            )
            print("(Info)~ Succeeded in removing message from SQS queue.")
        except Exception as exc:
            print("(Warning)~ Failed to delete the message from the SQS queue.")

    # Keep seeking messages until we have heard from all ids
    while len(ids) > 0:
        try:
            response = sqs.receive_message(
                QueueUrl=configs.ciAWSqueueNightly,
                # MessageAttributeNames=[instanceId,],
                VisibilityTimeout=5,  # 5 seconds are enough
                WaitTimeSeconds=20,  # Long-polling for messages, reduce number of empty receives
            )
        except Exception as exc:
            print_and_exit(f"(Error)~ Failed to receive a response from the SQS queue.")

        if "Messages" in response:
            for message in response["Messages"]:
                body = json.loads(message["Body"])
                instance_id = body["instance"]["id"]

                print(
                    f'(Info)~ { body["instance"]["id"] }, exited with status { body["job"]["status"] }. Comparing against { ids }'
                )

                # If we have a message about an ID we have to terminate, terminate it, and remove the message.
                if instance_id in ids:
                    ids.remove(instance_id)
                    terminate_instances(
                        [instance_id],
                        name,
                        int(body["job"]["node"]),
                        body["job"]["status"],
                    )
                    print(f"(Info)~ Removed Instance { instance_id }")

                delete_message(message)

        time.sleep(2)


def handle_init():
    # try:
    # Collect keys
    id = input("(Input)~ AWS Access Key ID: ")
    secret = input("(Input)~ AWS Secret Access Key: ")
    session = input("(Input)~ AWS Session Token: ")

    if id == "" or secret == "" or session == "":
        print_and_exit("(Error)~ At least one required input is empty.")

    # Collect region
    region = input("(Input)~ Default region name [us-west-2]: ")
    output = "json"

    region = region if region != "" else "us-west-2"

    # Write to credentials
    with open(os.path.expanduser("~/.aws/credentials"), "w") as f:
        f.write(
            f"[default]\naws_access_key_id = { id }\naws_secret_access_key = { secret }\naws_session_token = { session }"
        )

    # Write to config
    with open(os.path.expanduser("~/.aws/config"), "w") as f:
        f.write(f"[default]\nregion = { region }\noutput = { output }")

    # Export keys to zshrc
    with open(Path.home() / ".zshrc", "r+") as f:
        lines = f.readlines()
        zshrc = f'#~~~~~~~ AWS ~~~~~~~\nexport AWS_ACCESS_KEY_ID="{ id }"\nexport AWS_SECRET_ACCESS_KEY="{ secret }"\nexport AWS_SESSION_TOKEN="{ session }"'
        if "#~~~~~~~ AWS ~~~~~~~\n" in lines:
            i = lines.index("#~~~~~~~ AWS ~~~~~~~\n")
            non_aws = lines[0:i]
            non_aws_str = "".join(non_aws)
            zshrc = f"{ non_aws_str }{ zshrc }"
        else:
            lines_str = "".join(lines)
            zshrc = f"{ lines_str }\n\n{ zshrc }"
        f.seek(0)
        f.write(zshrc)
        f.truncate()

        # Source zshrc to update changes
        os.system("source " + str(Path.home()) + "/" + ".zshrc")

    # except Exception as e:
    #     if isinstance(e, OSError):
    #         print_and_exit(
    #             "(Error)~ AWS CLI is not installed.\n(Error)~ Visit https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html to install the required command line tools."
    #         )
    #     else:  # KeyboardInterrupt
    #         print_and_exit()


def start_instance(ami, name, i, branch, binaries_branch, key_path):

    global run_names

    print(f"(Info)~ Started start_instance with i={ i }")

    # Collect AWS Credentials from ~/.aws/credentials
    with open(os.path.expanduser("~/.aws/credentials"), "r") as f:
        lines = f.readlines()

    aws_creds = [line.split(" ")[2].strip() for line in lines[1:]]

    userdata_common = [
        "#!/bin/bash",
        "yum install -y git-lfs",
        "runuser -l centos -c 'sudo ssh-keyscan github.com >> ~/.ssh/known_hosts'",
        "cat >>/home/centos/.bashrc << EOL",
        f'export AWS_ACCESS_KEY_ID="{ aws_creds[0] }"',
        f'export AWS_SECRET_ACCESS_KEY="{ aws_creds[1] }"',
        f'export AWS_SESSION_TOKEN="{ aws_creds[2] }"',
        "EOL",
    ]

    # If either branch is specified, we need to get a SSH key - best solution so far
    if branch or binaries_branch:

        try:
            with open(os.path.expanduser(key_path), "r") as f:
                key = f.readlines()
                key = [x.strip() for x in key]
        except:
            print("(Error)~ Invalid Key Path")

        userdata_ssh = [
            "runuser -l centos -c 'touch /home/centos/.ssh/aws-ci-gh'",
            "cat >/home/centos/.ssh/aws-ci-gh <<EOL",
        ]
        userdata_ssh.extend(key)
        userdata_ssh.append("EOL")
        userdata_ssh.append(
            "runuser -l centos -c 'chmod 600 /home/centos/.ssh/aws-ci-gh'"
        )

    # Compose userdata contents, depending on whether path was specified.
    # Binaries branch and Target branch provided
    if branch and binaries_branch:
        userdata_specific = [
            f"""runuser -l centos -c 'ssh-agent bash -c "ssh-add /home/centos/.ssh/aws-ci-gh && 
                cd /home/centos/SSITH-FETT-Target/ && 
                git fetch &&
                cd SSITH-FETT-Binaries && 
                git stash && 
                cd .. && 
                git checkout { branch } && 
                git pull && 
                git submodule update && 
                cd SSITH-FETT-Binaries && 
                git checkout { binaries_branch } &&
                git pull &&
                git-lfs pull && 
                cd .. "'""",
            f"""runuser -l centos -c 'cd /home/centos/SSITH-FETT-Target && 
                nix-shell --command "ci/fett-ci.py -ep AWSNightly runDevPR -job { name }-{ i } -i { i }"' """,
        ]

        append_to_userdata(userdata_common)
        append_to_userdata(userdata_ssh)
        append_to_userdata(userdata_specific)

    # Only Target branch provided
    elif branch and not binaries_branch:
        userdata_specific = [
            f"""runuser -l centos -c 'ssh-agent bash -c "ssh-add /home/centos/.ssh/aws-ci-gh && 
                cd /home/centos/SSITH-FETT-Target/ && 
                git fetch &&
                cd SSITH-FETT-Binaries && 
                git stash && 
                cd .. && 
                git checkout { branch } && 
                git pull && 
                git submodule update && 
                cd SSITH-FETT-Binaries && 
                git-lfs pull && 
                cd .. "'""",
            f"""runuser -l centos -c 'cd /home/centos/SSITH-FETT-Target && 
                nix-shell --command "ci/fett-ci.py -ep AWSNightly runDevPR -job { name }-{ i }-{ branch }-{ run_names[i] } -i { i }"' """,
        ]

        append_to_userdata(userdata_common)
        append_to_userdata(userdata_ssh)
        append_to_userdata(userdata_specific)

    # Default branch on both
    else:
        lines = [
            f"""runuser -l centos -c 'cd /home/centos/SSITH-FETT-Target && 
            nix-shell --command "ci/fett-ci.py -ep AWSNightly runDevPR -job { name }-{ i }-{ run_names[i] } -i { i }"' """
        ]

        append_to_userdata(userdata_common)
        append_to_userdata(userdata_specific)

    print(
        f"(Info)~ Updated userdata.txt for { name }-{ i }.\n(Info)~ Launching instance and running tests...\n(Info)~ This process may take a few minutes."
    )

    # Start up an instance
    raw_payload = subprocess_check_output(
        f"aws ec2 run-instances --image-id { ami } --count 1 --instance-type f1.2xlarge --key-name nightly-testing --security-group-ids sg-047b87871fa61178f --subnet-id subnet-0ae96c15a09f122a1 --user-data file://$PWD/userdata.txt"
    )
    payload = json.loads(raw_payload)

    # Get instance ID From the return of AWS run-instance call
    id = payload["Instances"][0]["InstanceId"]

    # Add a name to our instance
    subprocess_check_output(
        f"aws ec2 create-tags --resources { id } --tags Key=Name,Value={ name }-{ i }"
    )

    print(f"(Info)~ Launched { name }-{ i } and running tests.")

    # Comment for debug
    os.remove("userdata.txt")
    print(f"(Info)~ Deleted userdata.txt for { name }-{ i }.")

    return id


def terminate_instances(ids, name, num, status):

    global run_names

    for i in range(len(ids)):
        print(
            f"(Result)~ { name }-{ num } [{ run_names[num] }] finished with status { status }. Logs are in nightly-testing-bucket."
        )
        with open("results.txt", "a") as f:
            f.write(f"{ run_names[num] } ({ num }) : { status }\n")

        subprocess_check_output(
            f"aws ec2 terminate-instances --instance-ids { ids[i] }"
        )
        print(f"(Info)~ Terminated { name }-{ num }.")


def config_parser():
    global run_names

    today = datetime.now().strftime("%m%d%y")

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "ami", type=str, help="AWS AMI ID to use, i.e. 'ami-xxxxxxxxxxxxxxxxxx'"
    )
    parser.add_argument(
        "-n",
        "--name",
        type=str,
        help="Base name to assign to instances created by this script (default is <current-date>-nightly)",
        default=f"{ today }-nightly",
    )
    parser.add_argument(
        "-i",
        "--init",
        help="Initialize (first run or if tokens have expired)",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        help="Number of Possible Comfigurations (same as length of the output of a dry run of the CI script).",
        default=len(run_names),
    )
    parser.add_argument(
        "-cp",
        "--cap",
        type=int,
        help="The maximum number of instances running at once (default is 1)",
        default=1,
    )
    parser.add_argument(
        "-b",
        "--branch",
        type=str,
        help="The branch of FETT-Target to check out on the AWS instance, and run tests on. Defaults to whatever is present on AMI",
    )
    parser.add_argument(
        "-bb",
        "--binaries-branch",
        type=str,
        help="The branch of FETT-Bineries to check out on the AWS instance, and run tests on. Defaults to whatever is present on AMI",
    )
    parser.add_argument(
        "-k",
        "--key-path",
        type=str,
        help='Path to the SSH key to be used with -b || -bb flags. Default: ["~/.ssh/aws-ci-gh"]',
        default="~/.ssh/aws-ci-gh",
    )
    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        help="How many complete runs of all targets to make. Default 1.",
        default=1,
    )
    parser.add_argument(
        "-idx",
        "--instance-index",
        type=int,
        help="Specify a specific index of target to run - if entered, this program will run $RUNS worth of this instance index only.",
    )
    return parser.parse_args()


def main():

    global run_names

    print("(Info)~ Welcome to the nightly testing command line app!")
    # try:

    # Test for presence of AWS CLI
    print("(Info)~ Testing AWS CLI...")
    subprocess_call("aws --version")
    print("(Info)~ AWS CLI installed!")

    # Generate run names list
    print("(Info)~ Gathering list of Launch Targets")
    collect_run_names()
    print(f"(Info)~ Done Gathering Targets")

    # Parse Arguments
    args = config_parser()

    if args.init:
        handle_init()
    else:
        with open(Path.home() / ".zshrc", "r") as f:
            lines = f.readlines()
            string = "".join(lines[-3:])

    ami = args.ami
    name = args.name
    count = args.count
    cap = args.cap
    branch = args.branch
    binaries_branch = args.binaries_branch
    key_path = args.key_path
    runs = args.runs
    instance_index = args.instance_index

    # Check for and remove results file
    if os.path.isfile("results.txt"):
        os.remove("results.txt")

    # Generate list of all launches - these are formatted as [run, index]
    to_run = []
    for run in range(1, runs + 1):
        if instance_index:
            to_run.append([run, instance_index])
        else:
            for x in range(0, count):
                to_run.append([run, x])

    # Fix to make sure that only one of the same instances is run at once
    #   the idx flag is passed
    if instance_index:
        cap = 1

    # Keep running batches until we have run them all
    while len(to_run) > 0:

        run_this_iteration = []
        ids = []

        # If there are fewer left in to_run than we have capacity, then run them all
        if len(to_run) <= cap:
            run_this_iteration = [y for y in to_run]
            to_run = []

        else:
            run_this_iteration = to_run[:cap]
            to_run = to_run[cap:]

        for launch in run_this_iteration:
            print(
                f"(Info)~ Launching Run { launch[0] }, Target { run_names[launch[1]] } ({ launch[1] })"
            )
            id = start_instance(ami, name, launch[1], branch, binaries_branch, key_path)
            ids.append(id)
            print(f"(Info)~ Launched Instance 🚀.")

            if instance_index:
                # Offset boots of the same instance to try to stagger SQS results
                #   to keep the messages from overloading.
                time.sleep(30)

        print("(Info)~ All Instances Launched! Waiting on SQS.")
        wait_on_ids_sqs(ids, name)
        print(f"(Info)~ Got SQS for all { len(run_this_iteration) } Instances")

        # Wait for the instances to terminate before running the next run
        if len(to_run) != 0:
            time.sleep(120)

    print(f"(Info)~ All { len(to_run) } Instances Completed. Exiting.")
    exit(0)

    # except Exception as e:
    #     if isinstance(e, KeyboardInterrupt):
    #         print_and_exit()
    #     elif isinstance(e, OSError):
    #         print_and_exit(
    #             "(Error)~ AWS CLI is not installed.\n(Error)~ Visit https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html to install the required command line tools."
    #         )
    #     else:
    #         err = str(e)
    #         print_and_exit(f"(Error)~ { err }")


if __name__ == "__main__":
    main()
