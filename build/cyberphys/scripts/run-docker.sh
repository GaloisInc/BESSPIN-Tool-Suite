#!/bin/bash
echo "This script should be run from the FETT target root directory"
sudo docker run --privileged=true -v $PWD:/home/besspinuser/target  --network host -it artifactory.galois.com:5008/fett-target:ci

