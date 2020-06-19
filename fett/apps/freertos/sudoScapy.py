#! /usr/bin/env python3
"""
TFTP/OTA tests using SCAPY to forge malicious TFTP packets
This program uses the SCAPY module so must be run as ROOT
"""

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
    if (na != 5):
        print ("\n<INVAID> Wrong number of arguments passed to sudoScapy.py\n")
        exit (0)
    print ("Args are:\n")
    print (sys.argv[0])
    print (sys.argv[1])
    print (sys.argv[2])
    print (sys.argv[3])
    print (sys.argv[4])

    # Restore the System Path of the calling program from sys.argv[1]
    parentPath = sys.argv[1].split('+')
    sys.path = list(set(sys.path + parentPath))
    # Now we can import Scapy
    import scapy.all as scapy

    try:
        spoofTFTP (sys.argv[2], sys.argv[3], int(sys.argv[4]))
    except:
        print ("\n<INVALID>: Failed to spoof TFTP\n")
    exit (0)
