#! /usr/bin/env python3
import struct
import socket
import select
import time
from can import BusABC, Message

from PyQt5 import QtWidgets, QtCore
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
import time
from random import randint


BIND_PORT = 5002
TX_PORT = 5001
TX_IP = "10.88.88.2"

class UDPBus(BusABC):
    """
    Enable basic communication over UDP

    The bus is bound to a particular ADDR and PORT upon creation,
    and can receive data only from that addr/port.

    The bus can send data to any address/port.
    """
    CAN_MIN_BYTES = 4 + 1 + 1  # sending an empty frame doesn't make sense, min 6 bytes per frame
    CAN_MAX_BYTES = 64 + 4 + 1  # 64 bytes of DATA, 4 bytes of ID, 1 byte od DLC

    def __init__(self, bind_port):
        self.port = bind_port
        super(UDPBus, self).__init__(channel="dummy")
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self._sock.bind(("", self.port))

    def send(self, msg, tx_ip, tx_port, timeout=None):
        a_id = struct.pack('<I', msg.arbitration_id)
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
            print("Info: received {} bytes from {}".format(len(rx_data), sender_addr))
            if len(rx_data) < UDPBus.CAN_MIN_BYTES:
                print("Warning: received only {} bytes, ignoring.".format(len(rx_data)))
            else:
                s = bytearray(rx_data[0:4])
                arb_id = struct.unpack('<I', s)[0]
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


# bus = UDPBus(BIND_PORT)
#
# # send a message
# message = Message(arbitration_id=0XAAFEEE00, is_extended_id=True,
#                   data=[0xAA, 0xBB, 0xCC, 0xDD])

# # iterate over received messages
# for msg in bus:
#     print(f"id={hex(msg.arbitration_id)}, data={msg.data}")
#     bus.send(message, TX_IP,TX_PORT)

ID_GEAR = 0xaa780280 # should be 0XAAF00500
ID_THROTTLE = 0xaa780d00 # should be 0XAAF01A00
ID_BRAKE = 0xaa780d80 # should be 0XAAF01B00

class MainWindow(QtWidgets.QMainWindow):
    labels = ['throttle', 'brake', 'gear']
    pen = pg.mkPen(color=(255, 0, 0),width=3)
    cnt = 0

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.graphWidget = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.graphWidget)
        self.resize(1420,1860)
        self.graphWidget.setBackground('w')

        self.xs = []
        self.ys = []
        self.lines = []
        self.axis = []
        self.starttime = time.time()

        for idx in range(0, len(self.labels)):
            ax = self.graphWidget.addPlot(row=idx, col=0)
            ax.showGrid(x = True, y = True, alpha = 1.0)
            ax.enableAutoScale()
            ax.setLabels(left=self.labels[idx])
            line = ax.plot(self.xs,[],pen=pg.mkPen('b', width=3))
            font=pg.QtGui.QFont()
            font.setPixelSize(25)
            font.setWeight(pg.QtGui.QFont.Bold)
            ax.getAxis("bottom").tickFont = font
            ax.getAxis("left").tickFont = font
            self.axis.append(ax)
            self.lines.append(line)
            self.ys.append([])

        self.bus = UDPBus(BIND_PORT)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)

    def update_data(self):
        wait_for_brake = True
        wait_for_throttle = True
        wait_for_gear = True

        gear = -420;
        brake = -420;
        throttle = -420;

        while wait_for_brake or wait_for_throttle or wait_for_gear:
            msg = self.bus.recv(timeout=0.1)
            if msg is not None:
                data = int.from_bytes(msg.data, byteorder='big', signed=False)
                print(f"ID={hex(msg.arbitration_id)}, value={data}, raw={msg.data}")
                if msg.arbitration_id == ID_GEAR:
                    gear = data
                    wait_for_gear = False
                elif msg.arbitration_id == ID_THROTTLE:
                    throttle = data
                    wait_for_throttle = False
                elif msg.arbitration_id == ID_BRAKE:
                    brake = data
                    wait_for_brake = False
                else:
                    print("Unknown ID")

        sim_time = time.time() - self.starttime
        self.xs.append(sim_time)
        self.ys[0].append(throttle)
        self.ys[1].append(brake)
        self.ys[2].append(gear)

        if len(self.xs) > 100:
            self.xs = self.xs[1:100]
            self.ys[0] = self.ys[0][1:100]
            self.ys[1] = self.ys[1][1:100]
            self.ys[2] = self.ys[2][1:100]

        for idx in range(0, len(self.lines)):
            self.lines[idx].setData(self.xs,self.ys[idx])


def threaded_plot_render():
    print("Starting live plot thread")
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

threaded_plot_render()