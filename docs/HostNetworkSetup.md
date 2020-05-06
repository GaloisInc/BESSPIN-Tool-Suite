# Host Network Setup

We expected the host machine to have a network interface called `eth0fpga` which is
connected to the FPGA and has a fixed IPv4 address of `10.88.88.1`. The FPGA then will have IP of `10.88.88.2`

Because each host machine might have different default names for the ethernet adaptors, we need to rename the proper interface. The best way is to use `crontab` and a custom script.

0. Make sure `macchanger` is installed:
    ```
    sudo apt install macchanger
    ```

1. In this case we have interface `enp3s0f1` connected to the FPGA. Change the   script accordingly for your machine:

    ```
    #!/bin/bash
    OLDNAME=enp3s0f1
    NEWNAME=eth0fpga
    ip link set $OLDNAME down
    ip link set $OLDNAME name $NEWNAME
    ip link set $NEWNAME up
    macchanger -m 88:53:48:41:56:45 $NEWNAME
    ip addr add 10.88.88.1/24 dev $NEWNAME
    ```

    and save it as `/opt/net_setup.sh`

2. Make executable:
    ```
    sudo chmod +x /opt/net_setup.sh
    ```

3. Edit crontab with:
    ```
    sudo crontab -e
    ```
    andd add:
    ```
    @reboot /opt/net_setup.sh
    ```

4. Check that the command got saved:
    ```
    sudo crontab -l
    # lists all cron jobs
    ...
    @reboot /opt/net_setup.sh
    ...
    ```

5. Reboot your computer. You should now see something like:
    ```
    ip a
    ...
    4: eth0fpga: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
        link/ether 88:53:48:41:56:45 brd ff:ff:ff:ff:ff:ff
        inet 10.88.88.1/24 scope global eth0fpga
    ...
    ```