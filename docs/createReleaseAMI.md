# Updating FETT Target AMI for a release

## Overview

This guide outlines how to updated an existing FETT-Target AMI for a newer release.

## Procedure

1. Open a PR to merge `develop` to `master`, and merge it. 

2. Get the hash of the master's tip. Let's say "1234567xxxxxxxxxxxxx".

3. Launch any instance (we often use c4.4xlarge) with the most recent `fett-target-centos-mmddyy-zzzzzzz` AMI.

4. Figure out your SSH keys situation to be able to `git pull`. Either by creating a new key and adding it to your github account, or by forwarding your keys from somewhere.

5. Update the tool's checkout:
```
cd ~/SSITH-FETT-Target
cd SSITH-FETT-Binaries
git stash
cd ..
git pull #this is assuming that we're on master (as we should)
git log -1 #check visually that the master's tip is correct
git submodule update
cd SSITH-FETT-Binaries
git lfs pull
```

6. Nix update:
```
cd ~/SSITH-FETT-Target
nix-shell
nix-shell$ nix-collect-garbage
nix-shell$ exit
nix-shell
nix-shell$ history -c
nix-shell$ exit
```

7. Clear your data (as explained in `FettAMI.md` step 13)
```
rm /home/centos/.gitconfig #you didn't need to put there anything anyway
rm ~/.ssh/*
rm ~/.bash_history
history -c
```

8. Create the AMI:
    - EC2 dashboard --> instances --> Stop your instance
    - Wait for it to show `stopped`
    - right click (or actions) --> Image --> Create Image
    - Name the AMI: `fett-target-centos-mmddyy-1234567` where `1234567` are the first 7 chars from the master's tip.
    - AMI description: `FETT AMI 1234567xxxxxxxxxxxxx`

9. Test the AMI:
    - Create a fresh `f1.2xlarge` based on the instance.
    - open nix-shell
    - Run: `ci/fett-ci.py -X runDevPR -ep AWS -job 123`
    - Now you have all the configs in `/tmp/dumpIni`. 
    - Create one instance per config, and launch that config and ensure that it gives `Success`.
    - If something fails, then after a fix is merged to master, all steps have to be repeated.
    - Please note ticket #516. Firesim target sometimes work on the third run (on the same instance).

10. Tag master branch:
On any machine, get the AMI ID, let's say `ami-xxxxxxxxxxxx`.
```
git checkout master
git pull
git tag v3.N-ami-xxxxxxxxxxx
git push --tags
```
Note that `N` is the next point release.

11. AMIs permissions:
    - EC2 dashboard --> AMIs --> select the AMI 
    - In the permissions tab (in the bottom), please add `065510690417` to the accounts with which this AMI is shared.
    - select the AMI --> right click --> copy AMI --> Destination reigion: N. Virginia --> Copy AMI
    - Change your region on the top right to `N. Virginia`
    - Wait for the AMI to be available
    - Share it with the production account `065510690417` as you did with the Oregon AMI

12. Send to FTS:
Send both AMI IDs to Kurt Hopfer and make sure he confirms the receipt.

## Additional Tasks ##

### CloudWatch ####

If you want to update the CloudWatch configuration, then before step 7 or 8, do the following:

- Kill the current cloudWatch process:
```
ps -A | grep cloud
sudo kill <PID-FROM-STEP-1>
```

- Update the `/opt/aws/amazon-cloudwatch-agent/bin/config.json` as you desire.

- Relaunch:
```
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
```