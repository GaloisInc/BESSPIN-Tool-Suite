#!/bin/bash
# TODO: convert to services instead
SESSIONNAME="adminpc"
tmux has-session -t $SESSIONNAME &> /dev/null
if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "bash" C-m
    tmux send-keys -t $SESSIONNAME "sudo /opt/net_setup.sh" C-m
    tmux send-keys -t $SESSIONNAME "ip a" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME "bash" C-m
    tmux send-keys -t $SESSIONNAME 'nix-shell' C-m
    tmux send-keys -t $SESSIONNAME './besspin.py -d -c besspin/cyberPhys/configs/config-cyberphys-freertos.ini' C-m
fi

# SESSIONNAME="infotainment"
# IP=10.88.88.2
# tmux has-session -t $SESSIONNAME &> /dev/null
# if [ $? != 0 ]
#  then
#     tmux new-session -s $SESSIONNAME -n script -d
#     tmux send-keys -t $SESSIONNAME "bash" C-m
#     tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
#     tmux send-keys -t $SESSIONNAME "ssh pi@${IP}" C-m
#     tmux send-keys -t $SESSIONNAME "tmux a -t ${SESSIONNAME}" C-m
# fi

# SESSIONNAME="hacker-kiosk"
# IP=10.88.88.3
# tmux has-session -t $SESSIONNAME &> /dev/null
# if [ $? != 0 ]
#  then
#     tmux new-session -s $SESSIONNAME -n script -d
#     tmux send-keys -t $SESSIONNAME "bash" C-m
#     tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
#     tmux send-keys -t $SESSIONNAME "ssh pi@${IP}" C-m
#     tmux send-keys -t $SESSIONNAME "tmux a -t ${SESSIONNAME}" C-m
# fi

# SESSIONNAME="can-display"
# IP=10.88.88.5
# tmux has-session -t $SESSIONNAME &> /dev/null
# if [ $? != 0 ]
#  then
#     tmux new-session -s $SESSIONNAME -n script -d
#     tmux send-keys -t $SESSIONNAME "bash" C-m
#     tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
#     tmux send-keys -t $SESSIONNAME "ssh pi@${IP}" C-m
#     tmux send-keys -t $SESSIONNAME "tmux a -t ${SESSIONNAME}" C-m
# fi

# SESSIONNAME="debian"
# IP=10.88.88.6
# tmux has-session -t $SESSIONNAME &> /dev/null
# if [ $? != 0 ]
#  then
#     tmux new-session -s $SESSIONNAME -n script -d
#     tmux send-keys -t $SESSIONNAME "bash" C-m
#     tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
#     tmux send-keys -t $SESSIONNAME "ssh galoisuser@${IP}" C-m
#     tmux send-keys -t $SESSIONNAME "tmux a -t ${SESSIONNAME}" C-m
# fi
