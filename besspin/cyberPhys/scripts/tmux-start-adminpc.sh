#!/bin/bash
SESSIONNAME="adminpc"
tmux has-session -t $SESSIONNAME &> /dev/null
if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "sudo /opt/net_setup.sh" C-m
    tmux send-keys -t $SESSIONNAME "ip a" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME 'nix-shell' C-m
    tmux send-keys -t $SESSIONNAME './besspin.py -d -c besspin/cyberPhys/configs/config-cyberphys-freertos.ini' C-m
fi

SESSIONNAME="infotainment"
IP=10.88.88.2
USER=pi
tmux has-session -t $SESSIONNAME &> /dev/null
if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
    tmux send-keys -t $SESSIONNAME "ssh ${USER}@${IP}" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl restart infotainment" C-m
    tmux send-keys -t $SESSIONNAME "systemctl status infotainment" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
    tmux send-keys -t $SESSIONNAME "ssh ${USER}@${IP}" C-m
    tmux send-keys -t $SESSIONNAME "sleep 20" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl restart infotainment-backend" C-m
    #tmux send-keys -t $SESSIONNAME "cd /home/pi/BESSPIN-Tool-Suite/besspin/cyberPhys/ui/infotainment" C-m
    #tmux send-keys -t $SESSIONNAME "python3 infotainment-backend.py" C-m
    tmux send-keys -t $SESSIONNAME "systemctl status infotainment-backend" C-m
fi

SESSIONNAME="hacker-kiosk"
IP=10.88.88.3
USER=galoisuser
tmux has-session -t $SESSIONNAME &> /dev/null
if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
    tmux send-keys -t $SESSIONNAME "ssh ${USER}@${IP}" C-m
    tmux send-keys -t $SESSIONNAME "/home/${USER}/mouse-config.sh" C-m
    tmux send-keys -t $SESSIONNAME "sleep 20" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl restart hacker-ui" C-m
    tmux send-keys -t $SESSIONNAME "sudo journalctl -fu hacker-ui" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
    tmux send-keys -t $SESSIONNAME "ssh ${USER}@${IP}" C-m
    tmux send-keys -t $SESSIONNAME "sleep 20" C-m
    #tmux send-keys -t $SESSIONNAME "sudo systemctl restart hacker-kiosk" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl stop hacker-kiosk" C-m
    tmux send-keys -t $SESSIONNAME "cd /home/${USER}/BESSPIN-Tool-Suite/besspin/cyberPhys/ui/hacker-kiosk" C-m
    tmux send-keys -t $SESSIONNAME "python3 kiosk-backend.py --deploy-mode" C-m
fi

SESSIONNAME="simPc"
IP=10.88.88.4
USER=galois
tmux has-session -t $SESSIONNAME &> /dev/null
if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
    tmux send-keys -t $SESSIONNAME "ssh ${USER}@${IP}" C-m
    tmux send-keys -t $SESSIONNAME "powershell.exe" C-m
fi

SESSIONNAME="can-display"
IP=10.88.88.5
USER=pi
tmux has-session -t $SESSIONNAME &> /dev/null
if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
    tmux send-keys -t $SESSIONNAME "ssh ${USER}@${IP}" C-m
    tmux send-keys -t $SESSIONNAME "sleep 20" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl restart can-ui" C-m
    tmux send-keys -t $SESSIONNAME "systemctl status can-ui" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
    tmux send-keys -t $SESSIONNAME "ssh ${USER}@${IP}" C-m
    tmux send-keys -t $SESSIONNAME "sleep 20" C-m
    tmux send-keys -t $SESSIONNAME "sudo systemctl restart can-display" C-m
    #tmux send-keys -t $SESSIONNAME "cd /home/pi/BESSPIN-Tool-Suite/besspin/cyberPhys/ui/can-display" C-m
    #tmux send-keys -t $SESSIONNAME "python3 can-display.py" C-m
    tmux send-keys -t $SESSIONNAME "systemctl status can-display" C-m
fi

SESSIONNAME="debian"
IP=10.88.88.6
USER=galoisuser
tmux has-session -t $SESSIONNAME &> /dev/null
if [ $? != 0 ]
 then
    tmux new-session -s $SESSIONNAME -n script -d
    tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
    tmux send-keys -t $SESSIONNAME "ssh ${USER}@${IP}" C-m
    tmux send-keys -t $SESSIONNAME "sudo /opt/net_setup.sh" C-m
    tmux send-keys -t $SESSIONNAME "ip a" C-m

    tmux split-window -h -t $SESSIONNAME
    tmux send-keys -t $SESSIONNAME "/opt/ping-until-available.sh ${IP}" C-m
    tmux send-keys -t $SESSIONNAME "ssh ${USER}@${IP}" C-m
    tmux send-keys -t $SESSIONNAME "cd BESSPIN-Tool-Suite" C-m
    tmux send-keys -t $SESSIONNAME 'nix-shell' C-m
    tmux send-keys -t $SESSIONNAME './besspin.py -d -c besspin/cyberPhys/configs/config-cyberphys-debian.ini' C-m
fi
