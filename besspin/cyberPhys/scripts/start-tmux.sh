#!/bin/bash
# Move to /opt/ and schedule to run after reboot with `crontab -e`
# Set to your BESSPIN-Tool-Suite dir, and proper tmux start script
cd /home/galoisuser/BESSPIN-Tool-Suite
/bin/bash ./besspin/cyberPhys/scripts/tmux-start-adminpc.sh
