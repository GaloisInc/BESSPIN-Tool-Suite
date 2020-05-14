# CI for SSITH-FETT-Target
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