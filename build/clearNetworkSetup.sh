#! /usr/bin/env bash

# copied from somewhere
is_ip() {
    local ip=$1
 
    if expr "$ip" : '[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*$' >/dev/null; then
        for i in 1 2 3 4; do
            if [ $(echo "$ip" | cut -d. -f$i) -gt 255 ]; then
                return 1
            fi
        done
        return 0
    else
        return 1
    fi
}

print_usage() {
    echo "./clearNetworkSetup target [2ndIP]"
}

if [ -z $1 ]; then 
    echo "ERROR: Please provide the target type."
    print_usage
    exit 1
fi

target=$1

if [ $target == 'aws' ]; then
    if [ -z $2 ]; then 
        echo "ERROR: Please provide the 2nd IP value."
        print_usage
        exit 1
    fi

    ipAddress=$2
    is_ip $ipAddress
    if [  $? -ne 0 ]; then
        echo "ERROR: Please provide a valid IP"
        exit 1
    fi

    sudo iptables --flush
    sudo iptables -t nat --flush
    sudo ip tuntap del mode tap dev tap0

    mainAdaptorName=$(ip -br addr | grep $ipAddress | awk '{ print $1 }')
    sudo ip addr del $ipAddress dev $mainAdaptorName

elif [ $target == 'qemu' ]; then
    sudo iptables --flush
    sudo iptables -t nat --flush
    for xTap in $(ip -br addr | grep "^tap.*" | awk '{ print $1 }'); do
        sudo ip tuntap del mode tap dev $xTap
    done
else
    echo "ERROR: target type has to be in { aws | qemu }."
    exit 1
fi 
