# CI for BESSPIN-Tool-Suite

## Regular CI

The CI for target platform for the SSITH FETT bug bounty exercise.

We have four types of jobs:
1. **runOnPush-$flavor:**
    - Trigger: Every push on any branch. Please use wisely.
    - Logic: N/A.
    - Source: All configs in `./ci/runOnPush-$flavor`.
2. **runDevPR-$flavor:**   
    - Trigger: Every push on an open PR to develop.
    - Logic: Key features and flows.
    - Source: All configs outlined in `appSets['runDevPR-$flavor']` in `./ci/configs.py`.

3. **runPeriodic-$flavor:**
    - Trigger: Scheduled to run nightly.
    - Logic: All features and flows.
    - Source: All configs outlined in `appSets['runPeriodic-$flavor']` in `./ci/configs.py`.

4. **runRelease-$flavor:** Same as periodic, but should be manually triggered.
    - Trigger: Manual only.
    - Logic: All features and flows.
    - Source: All configs outlined in `appSets['runRelease-$flavor']` in `./ci/configs.py`.

Flavors:
1. **unix:** Runs on machines tagged `docker-fpga`.
2. **freertos:** Runs on machines tagges `docker-fpga-io`.

## AWS Pseudo CI

### Setup

- Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- If you will specify a BESSPIN-Tool-Suite branch (`-b`) or a BESSPIN-LFS branch (`-bb`), create an SSH key (default named `~/.ssh/id_rsa`) and grant it access to your github and gitlab-ext accounts.

### Usage

1. Export your AWS keys into the shell you are using by copying item 1 from the `Command line or Programatic access` field of the AWS login page.

2.
```bash
usage: aws-pseudo-ci.py [-h] [-a AMI] [-b BRANCH] [-bb BINARIES_BRANCH] [-c CAP]
                         [-i [INSTANCE_INDICES [INSTANCE_INDICES ...]]]
                         [-k KEY_PATH] [-p PEM_KEY_NAME] [-n NAME] [-r RUNS]
                         [-m {fett,cwe,all}]
```

### Functioning

AWS Pseudo CI uses the bucket described in [configs.py](configs.py) for both communication between instances and `aws-pseudo-ci.py` (within the S3 bucket, these will be under the prefix `communications/`) and for posting artifacts (logs) under the prefix `artifacts/`.

### Results

Results will be printed to screen, and put into the file `results.txt`.

### Logs 

Logs will be writted to the file `aws-pseudo-ci.log`, and contain very detailed information about the execution of `aws-pseudo-ci.py` 