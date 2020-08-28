#! /usr/bin/env bash

sourceVariants=('' '-purecap' '-temporal')

for idx in ${!sourceVariants[@]}; do
    cp ../../SSITH-FETT-Binaries/SRI-Cambridge/osImages/qemu/kernel-cheri${sourceVariants[$idx]}.elf .
    cp ../../SSITH-FETT-Binaries/SRI-Cambridge/osImages/common/disk-image-cheri${sourceVariants[$idx]}.img.zst .
done
