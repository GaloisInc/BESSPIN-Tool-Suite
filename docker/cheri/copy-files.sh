#! /usr/bin/env bash
set -x

sourceVariants=('-default' '-purecap' '-temporal')

mntPath=/mnt/cheridisk
sudo mkdir -p $mntPath

for sourceVariant in "${sourceVariants[@]}"; do
    targetSuffix=${sourceVariant%-default}
    kernel=./kernel-cheri${sourceVariant}.elf
    diskImage=./disk-image-cheri${sourceVariant}.img
    cp ../../BESSPIN-LFS/SRI-Cambridge/osImages/qemu/kernel-cheri${targetSuffix}.elf ${kernel}
    cp ../../BESSPIN-LFS/SRI-Cambridge/osImages/common/disk-image-cheri${targetSuffix}.img.zst ${diskImage}.zst

    unzstd ${diskImage}.zst
    devLoop=$(sudo losetup -f --show -P ${diskImage})
    sudo mount -t ufs -o ufstype=ufs2,loop,ro ${devLoop}p1 $mntPath
    mkdir sysroot${sourceVariant}
    sudo cp -a $mntPath/lib $mntPath/usr sysroot${sourceVariant} 
    sudo umount $mntPath
    sudo losetup -d $devLoop
done
