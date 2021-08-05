#!/bin/bash
SESSIONNAME="cyberphys"
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
    tmux send-keys -t $SESSIONNAME './besspin.py -d -c besspin/cyberPhys/configs/config-cyberphys.ini' C-m
fi

SESSIONNAME="hacker"
tmux has-session -t $SESSIONNAME &> /dev/null

if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "bash" C-m
    tmux send-keys -t $SESSIONNAME "sleep 60" C-m
    tmux send-keys -t $SESSIONNAME "ssh pi@hacker-kiosk" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl restart hacker-ui" C-m
    tmux send-keys -t $SESSIONNAME "/home/pi/mouse-config.sh" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME "bash" C-m
    tmux send-keys -t $SESSIONNAME "sleep 60" C-m
    tmux send-keys -t $SESSIONNAME "ssh pi@hacker-kiosk" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl stop hacker-kiosk" C-m
    tmux send-keys -t $SESSIONNAME "cd BESSPIN-Tool-Suite/besspin/cyberPhys/ui/hacker-kiosk/" C-m
    tmux send-keys -t $SESSIONNAME "python3 kiosk-backend.py" C-m
fi

SESSIONNAME="display"
tmux has-session -t $SESSIONNAME &> /dev/null

if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "bash" C-m
    tmux send-keys -t $SESSIONNAME "sleep 60" C-m
    tmux send-keys -t $SESSIONNAME "ssh pi@can-display" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl restart can-ui" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME "bash" C-m
    tmux send-keys -t $SESSIONNAME "sleep 60" C-m
    tmux send-keys -t $SESSIONNAME "ssh pi@can-display" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl stop can-display" C-m
    tmux send-keys -t $SESSIONNAME "cd BESSPIN-Tool-Suite/besspin/cyberPhys/ui/can-display/" C-m
    tmux send-keys -t $SESSIONNAME "python3 can-display.py" C-m
fi
