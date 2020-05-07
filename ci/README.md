# CI for SSITH-FETT-Target
The CI for target platform for the SSITH FETT bug bounty exercise.

We have four types of jobs:
1. **runPush:** 
    - Trigger: Every push on any branch. Please use wisely.
    - Source: All configs in `./ci/runPush`.
    - Logic: N/A.
2. **runDevPR:**   
    - Trigger: Every push on an open PR to develop.
    - Source: All configs in `./ci/runDevPR`.
    - Logic: Key features and flows.
3. **runPeriodic:** 
    - Trigger: Scheduled to run nightly.
    - Source: All configs in `./ci/runPeriodic`.
    - Logic: All features and flows.
4. **runRelease:** Same as periodic, but should be manually triggered.
    - Trigger: Manual only.
    - Source: All configs in `./ci/runRelease`.
    - Logic: All features and flows.