#!/bin/bash
# This script pings the target $1 until it responds
# Used for waiting until the desired target is available
IP=$1
rc=1

# this function is called when Ctrl-C is sent
function trap_ctrlc ()
{
    # perform cleanup here
    echo "Ctrl-C caught...performing clean up"

    # exit shell script with error code 2
    # if omitted, shell script will continue execution
    exit 2
}

trap "trap_ctrlc" 2

while [[ $rc -gt 0 ]]
do
    ping -c 1 -w 1 $1
    rc=$?
done
echo "Pinging {$1} succesfull!"
