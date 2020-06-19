#! /usr/bin/env python3
"""
TFTP/OTA tests using SCAPY to forge malicious TFTP packets
This program uses the SCAPY module so must be run as ROOT
"""

import scapy.all as scapy

def spoofTFTP(hostIP, targetIP, TFTPPort):
    print (f"HostIP   is {hostIP}\n");
    print (f"TargetIP is {targetIP}\n");
    print (f"TFTPPort is {TFTPPort}\n");

    #attackString = bytearray.fromhex("6c 6d 63 6f 64 65 6d 6f 2e 68 74 6d 2e 73 69 67 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c  6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c e0 6d 1b c0 ec c8 01 c0 00").decode()

    a = scapy.IP(src=hostIP,dst=targetIP)
    b = a/scapy.UDP(sport=RandShort(),dport=TFTPPort)
    c = b/scapy.TFTP(op=2)

    # Send something friendly for now.
    d = c/scapy.TFTP_RRQ(filename="hello.txt",mode="octet")

    print ("Packet is")
    d.show()
    print (d)
    print ("Sending...")
    r = sr1(d, timeout=3, verbose=True)
    print ("Response is")
    print (r)
    # Much more to do here ..
    #  check r
    #  forge and send a DATA packet
    #  check acknowledgement of that
    return

if __name__ == '__main__':
    import sys
    na = len(sys.argv)
    print (f"Arg count is {na}")
    if (na != 4):
        print ("\n<INVAID> Wrong number of arguments passed to sudoScapy.py\n")
        exit (0)
    print ("Args are:\n")
    print (sys.argv[0])
    print (sys.argv[1])
    print (sys.argv[2])
    print (sys.argv[3])
    parentPath = sys.argv[1].split('+')
    sys.path = list(set(sys.path + parentPath))
    try:
        spoofTFTP (sys.argv[1], sys.argv[2], int(sys.argv[3]))
    except:
        print ("\n<INVALID>: Failed to spoof TFTP\n")
    exit (0)
