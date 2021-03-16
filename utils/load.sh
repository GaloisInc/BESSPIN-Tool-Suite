
sudo losetup -fP workDir/osImages/FreeRTOS.img
sudo mkdir /loopfs
sudo mount -o loop /dev/loop0 /loopfs

