#!/bin/bash

# To be run on the Admin PC after teach boot (sudo crontab -e)
# Sets the name of the ethernet iface to eth0fpga

function setEthDev {
    OLDNAME=$1
    NEWNAME=$2
    echo "Calling setEthDev with OLDNAME=${OLDNAME} and NEWNAME=${NEWNAME}"
    sudo ip link set $OLDNAME down
    sudo ip link set $OLDNAME name $NEWNAME
    sudo ip addr add 10.88.88.1/24 dev $NEWNAME
    sudo macchanger -m 88:53:48:41:56:45 $NEWNAME
    sudo ip link set $NEWNAME up
}

NEWNAME=eth0fpga
OLDNAME=enx0050b6e11983

setEthDev $OLDNAME $NEWNAME
if [ $? = 1 ]
    then
        setEthDev eth0 $NEWNAME
fi
