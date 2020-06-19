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

    basic_pkt = scapy.IP(src=hostIP,dst=targetIP)
    sport=scapy.RandShort()
    b = basic_pkt/scapy.UDP(sport=sport,dport=TFTPPort)
    c = b/scapy.TFTP(op=2)

    # Send something friendly for now.
    d = c/scapy.TFTP_RRQ(filename="hello.txt",mode="octet")

    print ("Packet is")
    d.show()
    print (d)
    print ("Sending...")
    r = scapy.sr1(d, timeout=3, verbose=True)

    r[scapy.UDP].dport = TFTPPort
    r = r.__class__(str(r))
    if scapy.TFTP_ERROR in r:
        print (r[scapy.TFTP_ERROR].errormsg)
        sys.exit(0)
    print ("Response is")
    print (r)

    dport = r[scapy.UDP].sport
    print ("Target DATA port is")
    print (dport)
    print ("Source DATA port is")
    print (sport)

    DATA=basic_pkt/scapy.UDP(sport=sport, dport=dport)/scapy.TFTP(op=3)/scapy.TFTP_DATA(block=1)/Raw(load="this is a test")
    r2 = scapy.sr1(DATA, timeout=3, verbose=True)
    r2 = r2.__class__(str(r2))
    print ("Response2 is")
    print (r2)

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
    except Exception as exc:
        errorAndLog ("Failed to spoof TFTP", exc=exc, doPrint=False)
    exit (0)
