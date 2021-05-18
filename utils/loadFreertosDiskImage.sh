#! /usr/bin/env bash

# Mounts `workDir/osImages/FreeRTOS.img` onto `/loopfs`

sudo losetup -fP workDir/osImages/FreeRTOS.img
sudo mkdir /loopfs
sudo mount -o loop /dev/loop0 /loopfs

