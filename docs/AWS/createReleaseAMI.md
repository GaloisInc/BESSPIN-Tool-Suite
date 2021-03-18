# Updating FETT Target AMI for a release

## Overview

This guide outlines how to updated an existing FETT-Target AMI for a newer release.

## Procedure

1. Open a PR to merge `develop` to `master`, and merge it. 

2. Get the hash of the master's tip. Let's say "1234567xxxxxxxxxxxxx".

3. Launch any instance (we often use c4.xlarge) with the most recent `fett-target-centos-mmddyy-zzzzzzz` AMI.

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
    - Use the `aws-testing-ci` utility to test the AMI.
    - Check how many slots are empty in `us-west-2` on `Galois_TA-2_dev` to determine the `C` (capacity) value. Note that the utility does not support other accounts/regions yet.
    - Run the following:
        ```
        ./aws-testing-ci.py -a ami-xxxxxxxxxxxx -c C -n <UseAMeaningfulName> -r 3
        ```
    - That would test each combination 3 times.
    - If something fails, then after a fix is merged to master, the tests should be repeated.

10. Tag master branch:
On any machine, get the AMI ID, let's say `ami-xxxxxxxxxxxx`.
```
git checkout master
git pull
git tag v3.N-ami-xxxxxxxxxxx
git push --tags
```
Note that `N` is the next point release.

11. Copy the AMI to Virginia.
    - select the AMI --> right click --> copy AMI --> Destination reigion: N. Virginia --> Copy AMI
    - Change your region on the top right to `N. Virginia`
    - Wait for the AMI to be available

12. AMIs permissions:
    - Add `065510690417` (production account) to the accounts with which both AMIs are shared.
    - Run the following twice: 1. The Oregon AMI with `--region us-west-2`. 2. The Virginia AMI with `--region us-east-1`.

    ```
    aws ec2 modify-image-attribute --region <REGION> --image-id <AMI-ID> --attribute launchPermission --operation-type add --user-ids 053515949713 065510690417 104428437022 127763453929 450440740352 494240662784 592505567353 803897408424 845509001885 910658170027 938711909478
    ```

13. Share with FTS.

## Additional Tasks ##

### CloudWatch ####

If you want to update the CloudWatch configuration, then before step 7 or 8, do the following:

- Kill the current cloudWatch process:
    ```
    sudo pkill cloud
    ```

- Update the `/opt/aws/amazon-cloudwatch-agent/bin/config.json` as you desire.

- Relaunch:
    ```
    sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -s -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json
    ```