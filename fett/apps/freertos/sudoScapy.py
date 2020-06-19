#! /usr/bin/env python3
"""
TFTP/OTA tests using SCAPY to forge malicious TFTP packets
This program uses the SCAPY module so must be run as ROOT
"""

def spoofTFTP(hostIP, targetIP, TFTPPort):
    print (f"HostIP   is {hostIP}\n");
    print (f"TargetIP is {targetIP}\n");
    print (f"TFTPPort is {TFTPPort}\n");

    #attackString = bytearray.fromhex("6c 6d 63 6f 64 65 6d 6f 2e 68 74 6d 2e 73 69 67 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c  6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c e0 6d 1b c0 ec c8 01 c0").decode()

    # demo_data is a forged OTA payload, consisting of 85 bytes:
    #   64 bytes of (incorrect) Ed25519 signature
    #   21 character ASCII String "This should not work\n"
    demo_data = bytearray.fromhex("93 cd 69 8a 13 bd e1 dc 4b 38 0e ad 2c 05 f2 15 7b 50 95 b8 b3 f7 1b 65 ed 60 05 ef 97 f1 de 0d b1 70 d7 55 f5 56 c7 41 5d 73 9d 78 4e d6 af 84 b6 ff 20 00 ff 73 33 ab 7d 5e c1 5f e9 e3 48 0b 54 68 69 73 20 73 68 6f 75 6c 64 20 6e 6f 74 20 77 6f 72 6b 0a").decode('latin_1')

    basic_pkt = scapy.IP(src=hostIP,dst=targetIP)
    sport = 49152 # arbitrary, but avoid use of scapy.RandShort()
    print(f"Host source port is {sport}")
    b = basic_pkt/scapy.UDP(sport=sport,dport=TFTPPort)
    c = b/scapy.TFTP(op=2)

    # Send something friendly for now.
    d = c/scapy.TFTP_RRQ(filename="hello.txt",mode="octet")

    print ("Packet is")
    d.show()
    print (d)
    print ("Sending...")
    r = None

    while not r or scapy.UDP not in r:
        r = scapy.sr1(d, timeout=3, verbose=True)

    print ("Response is")
    r.show()

    new_dport = r[scapy.UDP].sport
    new_sport = sport
    print ("Target DATA port is")
    print (new_dport)
    print ("Source DATA port is")
    print (new_sport)

    DATA = basic_pkt/scapy.UDP(sport=new_sport, dport=new_dport)/scapy.TFTP(op=3)/scapy.TFTP_DATA(block=1)/scapy.Raw(load=demo_data)
    print ("DATA is")
    DATA.show()

    r2 = None
    while not r2 or scapy.UDP not in r2:
        r2 = scapy.sr1(DATA, timeout=3, verbose=True)
    print ("Response2 is")
    r2.show()

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
