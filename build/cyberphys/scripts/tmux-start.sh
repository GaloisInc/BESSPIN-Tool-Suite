#!/bin/bash

SESSIONNAME="cyberphys"
tmux has-session -t $SESSIONNAME &> /dev/null

if [ $? != 0 ] 
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "bash" C-m
    tmux send-keys -t $SESSIONNAME "ip a" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME "bash" C-m
    tmux send-keys -t $SESSIONNAME 'nix-shell' C-m
    tmux send-keys -t $SESSIONNAME './fett.py -d -c build/cyberphys/configs/config-cyberphys.ini' C-m
fi

tmux attach -t $SESSIONNAME
