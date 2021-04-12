#! /usr/bin/env bash

# Undo what `loadFreeRTOSDiskImage.sh` does.
# Unmounds `/loopfs` and cleans the /dev/loop0 created.

sudo umount /loopfs
sudo rmdir /loopfs
sudo losetup -d /dev/loop0
