# CI for SSITH-FETT-Target
The CI for target platform for the SSITH FETT bug bounty exercise.

We have four types of jobs:
1. **runOnPush:** 
    - Trigger: Every push on any branch. Please use wisely.
    - Logic: N/A.
    - Source: All configs in `./ci/runOnPush`.
2. **runDevPR:**   
    - Trigger: Every push on an open PR to develop.
    - Logic: Key features and flows.
    - Source: All configs outlined in `appSets['runDevPR']` in `./ci/configs.py`.
    
3. **runPeriodic:** 
    - Trigger: Scheduled to run nightly.
    - Logic: All features and flows.
    - Source: All configs outlined in `appSets['runPeriodic']` in `./ci/configs.py`.
    
4. **runRelease:** Same as periodic, but should be manually triggered.
    - Trigger: Manual only.
    - Logic: All features and flows.
    - Source: All configs outlined in `appSets['runRelease']` in `./ci/configs.py`.