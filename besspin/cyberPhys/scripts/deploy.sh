#! /bin/bash
# "AdminPc" : "10.88.88.1",
# "InfotainmentThinClient" : "10.88.88.2",
# "HackerKiosk" : "10.88.88.3",
# "SimPc" : "10.88.88.4",
# "CanDisplay" : "10.88.88.5",
# "DebianPc" : "10.88.88.6"

for IP in 10.88.88.2 10.88.88.3 10.88.88.5 # InfotainmentThinClient | CanDisplay
do
	echo "Deploying to ${IP}"
	rsync --progress -a --exclude=.git/* --exclude=FreeRTOS --exclude=BESSPIN-LFS --exclude=BESSPIN-Environment --exclude=BESSPIN-Voter-Registration --exclude=workDir BESSPIN-Tool-Suite pi@${IP}:~/
    ssh pi@${IP} "cd /home/pi/BESSPIN-Tool-Suite/besspin/cyberPhys/cyberphyslib && sudo python3 setup.py install"
done

# HackerKiosk (needs BESSPIN-LFS)
IP=10.88.88.3
echo "Deploying to ${IP}"
rsync --progress -a --exclude=.git/* --exclude=FreeRTOS --exclude=BESSPIN-Environment --exclude=BESSPIN-Voter-Registration --exclude=workDir BESSPIN-Tool-Suite pi@${IP}:~/
ssh pi@${IP} "cd /home/pi/BESSPIN-Tool-Suite/besspin/cyberPhys/cyberphyslib && sudo python3 setup.py install"

echo "Deploying to NUC_2/DebianPc"
IP=10.88.88.6
rsync --progress -a --exclude=.git/* --exclude=workDir BESSPIN-Tool-Suite galoisuser@${IP}:~/
