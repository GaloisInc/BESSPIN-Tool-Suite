import struct
import socket
import select
import time
from can import BusABC, Message

class UDPBus(BusABC):
    """
    Enable basic communication over UDP

    The bus is bound to a particular ADDR and PORT upon creation,
    and can receive data only from that addr/port.

    The bus can send data to any address/port.
    """
    @staticmethod
    def check_network_list(net_list):
        """determine if a list of ips is a valid blacklist/whitelist. If valid, return it.
        Else, raise a value error
        :param net_list: list
        :return network list
        """
        try:
            if net_list:
                [socket.inet_aton(s) for s in net_list]
        except Exception:
            raise ValueError
        return net_list

    CAN_MIN_BYTES = 4 + 1 + 1  # sending an empty frame doesn't make sense, min 6 bytes per frame
    CAN_MAX_BYTES = 64 + 4 + 1  # 64 bytes of DATA, 4 bytes of ID, 1 byte od DLC

    def __init__(self, bind_ip, bind_port,
                 whitelist = None,
                 blacklist = None):
        super(UDPBus, self).__init__(channel="dummy")
        self._whitelist = self.check_network_list(whitelist)
        self._blacklist = self.check_network_list(blacklist)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.bind((bind_ip, bind_port))

    def send(self, msg, tx_ip, tx_port, timeout=None):
        a_id = struct.pack('!I', msg.arbitration_id)
        byte_msg = bytearray(a_id)
        byte_msg.append(msg.dlc)
        byte_msg += bytearray([msg.data[i] for i in range(0, msg.dlc)])
        if timeout:
            print("Warning: ignoring timeout {}".format(timeout))
        self._sock.sendto(byte_msg, (tx_ip, tx_port))

    def _recv_internal(self, timeout):
        ready = select.select([self._sock], [], [], timeout)
        if ready[0]:
            rx_data, sender_addr = self._sock.recvfrom(UDPBus.CAN_MAX_BYTES)
            # ignore received data following whitelist, blacklist policy
            if self.whitelist:
                if sender_addr not in self.whitelist:
                    return None, False
            if self.blacklist:
                if sender_addr in self.blacklist:
                    return None, False
            if len(rx_data) < UDPBus.CAN_MIN_BYTES:
                print("Warning: received only {} bytes, ignoring.".format(len(rx_data)))
            else:
                s = bytearray(rx_data[0:4])
                arb_id = struct.unpack('!I', s)[0]
                dlc = rx_data[4]
                if dlc == len(rx_data[5:]):
                    data = rx_data[5:]
                    msg = Message(timestamp=time.time(),
                                arbitration_id=arb_id,
                                dlc=dlc,
                                data=data)
                    return msg, False
                else:
                    print("Warning: DLC ({}) and the length of data ({}) don't match, ignoring.".format(dlc,len(rx_data)))
        return None, False

    @property
    def whitelist(self):
        return self._whitelist

    @whitelist.setter
    def whitelist(self, wl: NetworkListType):
        self._whitelist = self.check_network_list(wl)

    @property
    def blacklist(self):
        return self._blacklist

    @blacklist.setter
    def blacklist(self, bl: NetworkListType):
        self._blacklist = self.check_network_list(bl)
