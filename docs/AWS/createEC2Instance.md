# Firing up an FPGA machine on AWS

## General

1. Create/login to an AWS account.
2. Go to the "Management Console".
3. In the console, navigate to Services -> EC2.

## Keypairs

1. Within the EC2 Console, navigate to the "Network & Security" dropdown, in the left bar. 
2. Click "Create key pair", and enter a descriptive name, and select a format.

## Launching an Instance

1. Make sure to select a location (top right corner) where you have a capacity for F1 instances. Please note that the smallest F1 which is `f1.2xlarge` consumes 8 vCPUs.
2. Select Launch instance -> Launch Instance
3. Select "My AMIs", and select the most recent `fett-target-centos-mmddyy` AMI image.
4. From the "Filter By" menu, select "FPGA Instances" and choose the f1.2xlarge option (the smallest), then press "Next: Configure Instance Details"
5. For Galois internals, from the Network dropdown, select the "elew-firesim" network, from the Subnet, select the us-west-2a subnet, then click "Next: Storage". For anyone else, please make sure your network settings are configured so that you can ssh to the instance.
6. The storage should default to a 150GB SSD and a 470GB NVME SSD. Click "Next: Tags"
7. Click Add Tag, and Key: "Name", Value: whatever name you want to see when your box is referenced. Click "Next: Security Group"
8. For Galois internals, select "Select an existing security group" and select the "elew-firesim" group. For anyone else, please make sure you can ssh to the instance in addition to any other ports/protocols you need to access. For both, please click "Review and Launch".
9. Click launch, and you will be prompted to choose your keypair that you have created above.

## Connecting to the Instance

1. Find the IP in the running instances dashboard of the AWS EC2 Console
2. Recommended: Add this to a `~/.ssh/config` file: (alternatively, use `ssh -i <.pem-file> centos@<ip>`)
```
Host fett-fpga
        HostName <ip>
        IdentityFile <.pem-file>
        User centos
```

## Getting The Tool Running

1. Create an SSH key on the HOST
2. `git config --global user.email "<email>" && git config --global user.name "<username"`
3. Follow the instructions in the tool's readme for cloning and initializing the repo. Additionally, follow the instructions for creating the AMI and what is required for the `awsf1` target.

## Adding a Secondary IP Address

If you'd like to communicate with the target from another machine on the same
subnet (as explained in [remoteCommunicationWithTarget.md](./remoteCommunicationWithTarget.md)), you'll need to add a secondary IP address to the instance. 

1. From the Instances window of the EC2 Management Console, right click on the
   instance you'd like to add a secondary IP to.
2. Click "Networking" -> "Manage IP Addresses".
3. Click "Assign new IP".
4. Click "Yes, Update".  This will automatically generate a secondary IP.
5. Set `productionTargetIp` in the configuration file to the IP you just generated.

The tool will configure the target to be reachable at the secondary IP address from
the subnet the F1 instance is running on. However, the reachability of the
target will still be limited by your security group settings. You must ensure
your security group settings permit the traffic you'd like to facilitate to the
instance.  For example, if you'd like to be able to SSH into the target, you
must allow access to TCP port 22 in the instance's security group.

