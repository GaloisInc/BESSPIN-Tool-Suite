#! /usr/bin/env bash
set -x

sourceVariants=('' '-purecap' '-temporal')

mntPath=/mnt/cheridisk
sudo mkdir -p $mntPath

for idx in ${!sourceVariants[@]}; do
    cp ../../SSITH-FETT-Binaries/SRI-Cambridge/osImages/qemu/kernel-cheri${sourceVariants[$idx]}.elf .
    cp ../../SSITH-FETT-Binaries/SRI-Cambridge/osImages/common/disk-image-cheri${sourceVariants[$idx]}.img.zst .
    diskImage=./disk-image-cheri${sourceVariants[$idx]}.img

    echo "Extracting sysroot from ${diskImage}"
    unzstd ${diskImage}.zst
    devLoop=$(sudo losetup -f --show -P ${diskImage})
    sudo mount -t ufs -o ufstype=ufs2,loop,ro ${devLoop}p1 $mntPath
    mkdir sysroot${sourceVariants[$idx]}
    sudo cp -r $mntPath/lib $mntPath/usr sysroot${sourceVariants[$idx]} 
    sudo umount $mntPath
    sudo losetup -d $devLoop
done
