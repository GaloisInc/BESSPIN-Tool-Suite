# CI for SSITH-FETT-Target

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

## AWS Testing CI

### Setup

- Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- Create an SSH key (named `~/.ssh/aws-ci-gh`) and associate it with your github and gitlab-ext accounts - this will facilitate checking out the branches specified with the `-b` and `-bb` flags.

### Usage

1. Export your AWS keys into the shell you are using by copying item 1 from the `Command line or Programatic access` field of the AWS login page.

2.
```bash
usage: aws-testing-ci.py [-h] [-a AMI] [-b BRANCH] [-bb BINARIES_BRANCH]
                         [-c CAP]
                         [-idx [INSTANCE_INDICES [INSTANCE_INDICES ...]]]
                         [-k KEY_PATH] [-n NAME] [-r RUNS]
```

### Results

The results will be posted to the AWS S3 bucket described in [`configs.py`](configs.py), under the job name. Results will also be stored to `results.txt`, and logs will be written to `aws-test-suite.log`.