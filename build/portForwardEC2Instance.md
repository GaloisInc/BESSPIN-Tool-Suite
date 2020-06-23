# AWS FPGA Networking Setup


## Template Port Forwarding Command

```bash
sudo iptables -A FORWARD -i <HOST_ADAPTER> -o <TARGET_ADAPTER> -p tcp --syn --dport <TARGET_PORT> -m conntrack --ctstate NEW -j ACCEPT
sudo iptables -A FORWARD -i <HOST_ADAPTER> -o <TARGET_ADAPTER> -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A FORWARD -i <TARGET_ADAPTER> -o <HOST_ADAPTER> -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o <HOST_ADAPTER> -j MASQUERADE
sudo iptables -A PREROUTING -t nat -i <HOST_ADAPTER> -p tcp --dport <HOST_PORT> -j DNAT --to <FPGA_IP>:<TARGET_PORT>
sudo sysctl -w net.ipv4.ip_forward=1
```

`<FPGA_IP>` and `<TARGET_PORT>` are defined in [setupEnv.json](../fett/base/utils/setupEnv.json)
`<HOST_PORT>` is defined by you, however it must be within the range of ports allowed by the AWS Security Group applied to your AWS instance.
`<HOST_ADAPTER>` and `<TARGET_ADAPTER>` are found using `ip a` on the HOST.

When the OS is booted on the FPGA (and provided it is an OS that supports this), you should be able to `ssh` from the HOST to the TARGET (`root@<FPGA_IP>`) with no port forwarding rules.

### Alternative Template Command

```bash
sudo iptables -A FORWARD -i <HOST_ADAPTER>  -o <TARGET_ADAPTER> -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i <TARGET_ADAPTER> -o <HOST_ADAPTER> -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o <HOST_ADAPTER> -j MASQUERADE
sudo iptables -A PREROUTING -t nat -i <HOST_ADAPTER> -p tcp --dport <HOST_PORT> -j DNAT --to <FPGA_IP>:<TARGET_PORT>
sudo iptables -P FORWARD ACCEPT
sudo sysctl -w net.ipv4.ip_forward=1
```

## Example Port Forwarding for SSH on AWS

In this example we forward inbound `ssh` connections (to port 10022, on the HOST) to `ssh` port 22 on the TARGET.

These commands correspond with these parameters on either 'template command':

- `<HOST_ADAPTER>`: `eth0` 
- `<HOST_PORT>`: `10022`
- `<TARGET_ADAPTER>`: `tap0`
- `<TARGET_PORT>`: `22`
- `<FPGA_IP>`: `172.16.0.2`

On the TARGET, run these commands (note IP and subnet mask are for the `aws` fpga):

```bash
ip route add default via 172.16.0.1
ping 4.2.2.1
```
On the HOST, run these commands:

```bash
sudo iptables -A FORWARD -i ens3 -o tap0 -p tcp --syn --dport 22 -m conntrack --ctstate NEW -j ACCEPT
sudo iptables -A FORWARD -i ens3 -o tap0 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A FORWARD -i tap0 -o ens3 -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE
sudo iptables -A PREROUTING -t nat -i ens3 -p tcp --dport 10022 -j DNAT --to 172.16.0.2:22
sudo sysctl -w net.ipv4.ip_forward=1
```

Alternative HOST commands:

```bash
sudo iptables -A FORWARD -i ens3  -o tap0 -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -i tap0 -o ens3 -j ACCEPT
sudo iptables -t nat -A POSTROUTING -o ens3 -j MASQUERADE
sudo iptables -A PREROUTING -t nat -i ens3 -p tcp --dport 10022 -j DNAT --to 172.16.0.2:22
sudo iptables -P FORWARD ACCEPT
sudo sysctl -w net.ipv4.ip_forward=1
```

Now that these rules are in place, to SSH into the TARGET from outside the HOST, do

```bash
ssh -p <HOST_PORT> researcher@<AWS_INSTANCE_IP>
```

## Example: Forwarding `nginx` Server

As a second example, we would use similar parameters to those for SSH, with a different port. 

- `<HOST_ADAPTER>`: `eth0` 
- `<HOST_PORT>`: `10081`
- `<TARGET_ADAPTER>`: `tap0`
- `<TARGET_PORT>`: `81`
- `<FPGA_IP>`: `172.16.0.2`

## Troubleshooting

### Clear `iptables` Entries

To clear the current `iptables` entries, use

```bash
sudo iptables -F
sudo iptables -t nat -F
```

### Check `iptables` Entries

```bash
sudo iptables -t nat -vnL
```

### Cannot `ping` out from TARGET

Try running the following to cycle the interface. 

```bash
ip link set dev eth0 down
ip link set dev eth0 up
ip addr add 172.16.0.2/24 dev eth0
ip route add default via 172.16.0.1
ping 4.2.2.1
```

Also check up on `ip a` 