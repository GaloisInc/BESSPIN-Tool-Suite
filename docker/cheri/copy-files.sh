#!/bin/sh

aws s3 cp s3://ta1-toolchain-images/cheri-sysroot.tar.gz .
cp ../../SSITH-FETT-Binaries/SRI-Cambridge/osImages/qemu/kernel-cheri.elf .
cp ../../SSITH-FETT-Binaries/SRI-Cambridge/osImages/common/disk-image-cheri.img.zst .
