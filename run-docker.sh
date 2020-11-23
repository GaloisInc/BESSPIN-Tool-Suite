#!/bin/bash
sudo docker run --privileged=true -v $PWD:/home/besspinuser/target  --network host -it artifactory.galois.com:5008/fett-target:ci

