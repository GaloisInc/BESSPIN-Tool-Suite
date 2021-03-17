# The Tool on AWS #

*Disambiguation:* For using the `awsf1` target, please refer to [targets.md](../base/targets.md).

This directory includes the following:

- **`buildConnectalBinaries.md`:** Reproduce the builds of the Connectal binary and required kernel modules.

- **`buildFireSimBinaries.md`:** Reproduce the builds of the Firesim binaries and required kernel modules.

- **`createEC2Instance.md`:** How to launch an F1 instance to be able to run the tool in `awsf1` mode.

- **`createFettAMI.md`:** Steps to create the tool's AMI from the generic FPGA dev AWS AMI.

- **`createFettAMI.md`:** Steps to update the tool's AMI for a release.

- **`remoteCommunicationWithTarget.md`:** How to communicate with the FPGA target from a different AWS instance (other than the host) or even a different computer given that the networking is properly handled.