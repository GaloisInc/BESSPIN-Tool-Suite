# How to communicate with the target from a different instance?

## Overview

This guide explains how to create a different instance (let's say `i-2`), and communicate with the target that is living on `i-1`. This is helpful to simulate the communication through NAT.

Note that `i-1` has to be an F1 instance, naturally, but `i-2` can be of any type. We often use `t2.micro` to limit the number of running vCPUs.

## Procedure

1. Follow the instructions in [createEC2Instance.md](./createEC2Instance.md) to launch a FETT AMI on an `f1.2xlarge` instance; this is the instance to which this document refers as `i-1`. Please pay attention to the last section of that document *Adding a Secondary IPAddress*. This can either be added while creating the instance, or added afterwards. This secondary IP is important. Let's call it `192.168.0.IP`.

2. If you have already run the tool on your instance (or have the tap adaptor configured for any reason), then you have to delete the `tap` adaptor:
```
sudo ip tuntap del mode tap dev tap0
```

3. For FETT's `.ini` config file, add your second IP:
```
>>> productionTargetIp = 192.168.0.IP
```

4. Run the tool in any open ended mode (`openConsole` or `production`).

5. Create another instance `i-2` in the same VPC and same subnet as `i-1`. Use any AMI, any instance type. It's easier to just use the FETT AMI on a `t2.micro`. 

6. Make sure the security group on both `i-1` and `i-2` enable any communication you are trying to do. For example, to use the OTA server, you need to enable UDP communication, both inbound and outbound, on both instances. For outbound from `i-1`, the inbound port range is `69`, while the outbound range is `49152-65280` (and vice versa on `i-2`). For inbound, this depends on the `i-2` OS. The easiest approach is to just open all UDP ports both ways. Another example is Michigan HTTP server, you have to open TCP port `9443`. For pinging, you have to explicitly enable `ICMP` in the security groups.

7. From `i-2`, you can just:
```
ping -c 1 192.168.0.IP
```
and that's it, the target is accessible.

