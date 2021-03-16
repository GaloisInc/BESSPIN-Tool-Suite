#! /usr/bin/env bash
sudo umount /loopfs
sudo rmdir /loopfs
sudo losetup -d /dev/loop0
