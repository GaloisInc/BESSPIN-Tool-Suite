#! /bin/bash
# TODO: add fixed IP values to avoid dependency on local DNS
for IP in hacker-kiosk can-display
do
	echo "Deploying to ${IP}"
	rsync --progress -a --exclude=.git/* --exclude=FreeRTOS --exclude=workDir BESSPIN-Tool-Suite pi@${IP}:~/
    ssh pi@${IP} "cd /home/pi/BESSPIN-Tool-Suite/besspin/cyberPhys/cyberphyslib && sudo python3 setup.py install"
done
