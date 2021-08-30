#!/bin/bash
SESSIONNAME="debian"
tmux has-session -t $SESSIONNAME &> /dev/null
if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "sudo /opt/net_setup.sh" C-m
    tmux send-keys -t $SESSIONNAME "ip a" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME 'nix-shell' C-m
    tmux send-keys -t $SESSIONNAME './besspin.py -d -c besspin/cyberPhys/configs/config-cyberphys-debian.ini' C-m
fi
