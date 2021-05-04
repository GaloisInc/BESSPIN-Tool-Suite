# Continuous Integration Readme

## Glossary

This is a work-in-progress glossary, so we can talk about the same thing.

* [Amazon FPGA Image (AFI)](https://github.com/aws/aws-fpga/tree/master/Vitis#createafi) - a bitstream, or a bitstream with an application (such as a bootloader), that is converted into "Amazon-compatible" format (through Amazon HDK or Vivado)
* [Amazon Machine Image (AMI)](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instances-and-amis.html) is a template that contains a software configuration (for example, an operating system, an application server, and applications). From an AMI, you launch an instance, which is a copy of the AMI running as a virtual server in the cloud.

    Our AMI will likely be based on Debian 10, and contain docker engine - so we can start a [Tool-Suite docker image](https://github.com/GaloisInc/BESSPIN-Environment/tree/master/docker/tool-suite). Some additional drivers from Amazon HDK might be necessary as well. Finally, specific network setup might be necessary so the docker image can always find the correct interface (we might have to rename a network interface for example)
* [BESSPIN-Environment](https://github.com/GaloisInc/BESSPIN-Environment) is a tool (it uses [nix package manager](https://nixos.org/nix/manual/)) that lets you set up a very reproducible environment (specific package versions, toolchains, bitstreams, applications,...). It can either build packages on demand, or pull prebuild versions from various sources.
* [BESSPIN-Tool-Suite](https://github.com/GaloisInc/BESSPIN-Tool-Suite/) is a platform build on top of [BESSPIN-Environment](https://github.com/GaloisInc/BESSPIN-Environment). It includes test scripts, configuration tools, etc.
* [Tool-Suite docker image](https://github.com/GaloisInc/BESSPIN-Environment/tree/master/docker/tool-suite) is a docker image that includes all the dependencies for [BESSPIN-Tool-Suite](https://github.com/GaloisInc/BESSPIN-Tool-Suite/), plus Vivado and other tools necessary to connect to the on-prem FPGA
* [BESSPIN-CloudGFE](https://github.com/GaloisInc/BESSPIN-CloudGFE/) is a repository containing hardware design and build scripts that generate cloudGFE bitstreams (or potentially even a finished AFI)

## Use cases

**NOTE:** these use cases are Work In Progress and are meant to start a discussion, rather than provide a definite answer about how things are done. Please treat them as such.

### CloudGFE development & testing

* [CloudGFE](https://github.com/GaloisInc/BESSPIN-CloudGFE/) will likely contain a BESSPIN-Tool-Suite as a submodule
* When a developer wants to run tests on new or modified HW design, it can be achieved by a call to `besspin.py` in BESSPIN-Tool-Suite submodule, with an appropriate config.
* Similarly, a subset of configs to be tested will be included in the CI configuration of CloudGFE  


### BESSPIN-Tool-Suite testing

BESSPIN-Tool-Suite includes a set of baseline bitstreams that are considered *stable*, much in the same way as *tool-suite* included bitstreams from a specific GFE release.

BESSPIN-Tool-Suite can also use a bitstream that is passed to it as a parameter, hence allow testing of arbitrary bitstreams.

BESSPIN-Tool-Suite will contain scripts for creating AFIs and spinning up/tearing down F1 instances. Hence deploying a bitstram on F1 can be as simple as running `besspin.py` with the appropriate config.



## Building bitstreams
We have one docker image `artifactory.galois.com:5008/vivado-sdk-2019-1` (see [here](https://github.com/GaloisInc/BESSPIN-Environment/tree/master/docker/vivado-sdk-2019-1)) and depending on which MAC address you set it to, it will enable either regular GFE license, or the AWS-ready license (with bitstream encryption). Below is an example how to generate two different (GFE vs CloudGFE) bitstreams in the [GFE repository](https://github.com/GaloisInc/BESSPIN-GFE/). This can serve as a good starting point when exploring how to turn the *cloud-ready* bitstreams into AFIs.


### Non-cloud GFE

Start in `gfe` root directory
```
$ git checkout develop
$ sudo docker run --mac-address="88:53:48:41:56:45" -it -v $PWD:/gfe artifactory.galois.com:5008/vivado-sdk-2019-1
$ rm -rf vivado
$ ./setup_soc_project.sh chisel_p1
$ ./build.sh chisel_p1
```

### AWS/Cloud GFE

Start in `gfe` root directory
```
$ git checkout aws-gfe
$ sudo docker run --mac-address="00:4E:01:B6:DD:79" -it -v $PWD:/gfe artifactory.galois.com:5008/vivado-sdk-2018-3
$ rm -rf vivado
$ ./setup_soc_project.sh aws_helloworld
$ ./build.sh aws_helloworld
```