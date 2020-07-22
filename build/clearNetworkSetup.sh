#! /usr/bin/env bash

if [ -z $1 ]; then 
    echo "ERROR: Please provide the 2nd IP value."
    exit 1
fi

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

ipAddress=$1
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
