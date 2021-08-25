#!/bin/bash
# To be run on the NUC after teach boot (sudo crontab -e)
# Sets the name of the ethernet iface to eth0fpga
# NOTE: change IP as needed
OLDNAME=eno1
NEWNAME=eth0fpga
IP=10.88.88.1
echo "Calling setEthDev with OLDNAME=${OLDNAME} and NEWNAME=${NEWNAME}"
sudo ip link set $OLDNAME down
sudo ip link set $OLDNAME name $NEWNAME
sudo ip addr add $IP/24 dev $NEWNAME
sudo ip link set $NEWNAME up
