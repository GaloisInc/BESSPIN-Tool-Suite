#! /usr/bin/env python3

"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has to be executed using sudo
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

def spoofIp (ipTarget, portTarget, spoofingIP):
    print (">>> [host-client-spoofing]: Attempting the spoof...\n")

    randPort = scapy.RandShort() # source port
    payload = "SSITH LORD" # packet payload

    for j in range(1):
        spoofed_packet = scapy.IP(src=spoofingIP, dst=ipTarget) / scapy.UDP(sport=randPort, dport=portTarget) / scapy.Raw(load=payload)
        scapy.send(spoofed_packet)

    print (">>> [host-client-spoofing]: Packet sent!\n")

if __name__ == '__main__':
    import sys
    if (len(sys.argv) != 5):
        print ("\n<INVAID> [host-client-spoofing]: Wrong number of arguments passed to sudo_290.py\n")
        exit (0)
    parentPath = sys.argv[1].split('+')
    sys.path = list(set(sys.path + parentPath))
    import scapy.all as scapy
    try:
        spoofIp (sys.argv[2], int(sys.argv[3]), sys.argv[4])
    except:
        print ("\n<INVALID> [host-client-spoofing]: Failed to send a spoofed packet!\n")
    exit (0)