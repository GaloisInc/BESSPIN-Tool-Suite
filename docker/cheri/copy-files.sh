#! /usr/bin/env bash
set -x

sourceVariants=('' '-purecap' '-temporal')

mntPath=/mnt/cheridisk
sudo mkdir -p $mntPath

for sourceVariant in "${sourceVariants[@]}"; do
    cp ../../SSITH-FETT-Binaries/SRI-Cambridge/osImages/qemu/kernel-cheri${sourceVariant}.elf .
    cp ../../SSITH-FETT-Binaries/SRI-Cambridge/osImages/common/disk-image-cheri${sourceVariant}.img.zst .
    diskImage=./disk-image-cheri${sourceVariant}.img

    unzstd ${diskImage}.zst
    devLoop=$(sudo losetup -f --show -P ${diskImage})
    sudo mount -t ufs -o ufstype=ufs2,loop,ro ${devLoop}p1 $mntPath
    mkdir sysroot${sourceVariant}
    sudo cp -a $mntPath/lib $mntPath/usr sysroot${sourceVariant} 
    sudo umount $mntPath
    sudo losetup -d $devLoop
done
