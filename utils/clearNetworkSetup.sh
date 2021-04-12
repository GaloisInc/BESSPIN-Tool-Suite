#! /usr/bin/env bash

# Clears network setups
#  ./clearNetworkSetup target [2ndIP]
#  target: String in [aws, qemu]
#  2ndIP: Only applicable when target==aws. The remoteTargetIp

#  If target==aws:
#     flushes all iptables and NAT rules
#     deletes the tap adaptor <tap0>
#     deletes the remoteTargetIp from main adaptor
#  If target==qemu:
#     flushes all iptables and NAT rules
#     deletes any adaptor that starts with a 't' AND whose IP address starts with "172.16"

is_ip() {
    # copied from somewhere
    # ARGUMENTS:
    # ----------
    # $1: String
    #       An input IP address string
    #
    # RETURN:
    # -------
    # Integer (0/1): Whether the input string is a valid IP address (based on regex) 
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
    for xTap in $(ip -br addr | grep "^t.*" | awk '{ print $1 }'); do
        ipAddr=$(ip -br addr show $xTap | awk '{ print $3 }')
        network=$(echo "$ipAddr" | cut -d '.' -f1,2)
        if [ ! -z $network ] && [ $network == '172.16' ]; then
            echo "Deleting $xTap..."
            sudo ip tuntap del mode tap dev $xTap
        fi
    done
else
    echo "ERROR: target type has to be in { aws | qemu }."
    exit 1
fi 
