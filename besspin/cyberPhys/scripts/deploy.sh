#!/bin/bash
# "AdminPc" : "10.88.88.1",
# "InfotainmentThinClient" : "10.88.88.2",
# "HackerKiosk" : "10.88.88.3",
# "SimPc" : "10.88.88.4",
# "CanDisplay" : "10.88.88.5",
# "DebianPc" : "10.88.88.6"

# USER=pi
# for IP in 10.88.88.2 10.88.88.5 # InfotainmentThinClient | CanDisplay
# do
# 	echo "Deploying to ${IP}"
# 	rsync --progress -a --exclude=.git/* --exclude=FreeRTOS --exclude=BESSPIN-LFS --exclude=BESSPIN-Environment --exclude=BESSPIN-Voter-Registration --exclude=workDir BESSPIN-Tool-Suite ${USER}@${IP}:~/
# 	ssh ${USER}@${IP} "cd /home/pi/BESSPIN-Tool-Suite/besspin/cyberPhys/cyberphyslib && sudo python3 setup.py install"
# done

# HackerKiosk (needs BESSPIN-LFS)
USER=galoisuser
IP=10.88.88.3
echo "Deploying to ${IP}"
scp -r ./BESSPIN-Tool-Suite/besspin/cyberPhys/cyberphyslib ${USER}@${IP}:~/BESSPIN-Tool-Suite/besspin/cyberPhys
#ssh ${USER}@${IP} "cd /home/galoisuser/BESSPIN-Tool-Suite/besspin/cyberPhys/cyberphyslib && sudo python3 setup.py install"

# # Debian / Hacked Infotainment Server
# USER=galoisuser
# IP=10.88.88.6
# echo "Deploying to ${IP}"
# scp -r ./BESSPIN-Tool-Suite/besspin/cyberPhys/infotainment-server ${USER}@${IP}:~/BESSPIN-Tool-Suite/besspin/cyberPhys


# # AdminPC
# IP=10.88.88.1
# echo "Deploying to ${IP}"
# rsync --progress -a --exclude=.git/* --exclude=FreeRTOS --exclude=BESSPIN-Environment --exclude=BESSPIN-Voter-Registration --exclude=workDir BESSPIN-Tool-Suite ${USER}@${IP}:~/

# NOTE: no need to use NUC_2 for the exhibit
# echo "Deploying to NUC_2/DebianPc"
# IP=10.88.88.6
# rsync --progress -a --exclude=.git/* --exclude=workDir BESSPIN-Tool-Suite galoisuser@${IP}:~/

# SimPC
# For cyberphyslib only
#scp -o IdentitiesOnly=yes -r ./besspin/cyberPhys/cyberphyslib/ galois@10.88.88.4:"C:\Users\galois\BESSPIN-Tool-Suite\besspin\cyberPhys"

#scp -o IdentitiesOnly=yes -r  galois@10.88.88.4:"C:\Users\galois\BESSPIN-Tool-Suite\besspin\cyberPhys\cyberphyslib" ./winbackup/
