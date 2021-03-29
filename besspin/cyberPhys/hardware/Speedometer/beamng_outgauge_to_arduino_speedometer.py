'''
Project: SSITH CyberPhysical Demonstrator
Name: beamng_outgauge_to_arduino_speedometer.py
Author: Kristofer Dobelstein
Date: 18 August 2020

Python: 3.8.3
O/S: Windows 10

This routine is a bridge between BeamNG's Outgauge socket and an Arduino Micro-
based Smartcar speedometer. It provides the following functionality:

1. Listens to Outgauge from BeamNG on 127.0.0.1, port 4444
2. Unpacks the Outgauge struct
3. Prints few parameters to the console
4. Sends speed in miles per hour to the speedometer as a utf-8 encoded string
with a new line character.
5. Listens for any information sent from the speedometer (e.g., RIGHT for when
the right button is pressed.
'''

import sys
import socket
import struct
import binascii
from time import sleep
import serial
import serial.tools.list_ports

def transmission_gear(udp_gear):
    switcher = {
    '00':'R',
    '01':'N',
    '02':'D1',
    '03':'D2',
    '04':'D3',
    '05':'D4',
    '06':'D5',
    '07':'D6',
    '08':'D7',
    '09':'D8'}
    return switcher.get(udp_gear, "invalid")

# socket parameters
UDP_IP = "127.0.0.1"
UDP_PORT = 4444

# create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # internet + udp
sock.bind((UDP_IP, UDP_PORT))

# scan active serial ports to find where the first Arduino Micro is attached
# since this is a fixed system, we know there's only one present
speedometer_com_port = ''
com_ports = list(serial.tools.list_ports.comports())

# set a flag to track the presence of a USB speedometer
usb_speedometer_present = False

# look for an Arduino Micro and find its port number
for p in com_ports:
    if "Arduino Micro" in p.description:
        speedometer_com_port = str(p.device)
        usb_speedometer_present = True

# if we don't find an Arduino Micro, tell the user and exit the script
if usb_speedometer_present is False:
    print('Could not find Smartcar USB Speedometer. Exiting the script.')
    sys.exit()

# try to create a serial port object for the interface with the Arduino-based
# speedometer instrument cluster
try:
    arduino = serial.Serial(port=speedometer_com_port,
	                        baudrate=38400,
							timeout=0.05)
    arduino.flushInput()
    sleep(1)
# if no speedometer, print an error to the console and exit the script.  
except:
    print('Could not create serial COM port connection to Smartcar USB Speedometer. Exiting the script.')    	
    sys.exit()

# main loop
while True:
    data = sock.recv(96)
    # Outgauge packet is documented here: https://www.brunsware.de/insim/structOutGaugePack.html
    outgauge_pack = struct.unpack('I4sH2c7f2I3f16s16si', data)
    time = outgauge_pack[0]
    car = outgauge_pack[1]
    flags = outgauge_pack[2]
    gear = outgauge_pack[3]
    plid = outgauge_pack[4]
    speed = outgauge_pack[5]
    rpm = outgauge_pack[6]
    turbo = outgauge_pack[7]
    engtemp = outgauge_pack[8]
    fuel = outgauge_pack[9]
    oilpressure = outgauge_pack[10]
    oiltemp = outgauge_pack[11]
    dashlights = outgauge_pack[12]
    showlights = outgauge_pack[13]
    throttle = outgauge_pack[14]
    brake = outgauge_pack[15]
    clutch = outgauge_pack[16]
    display1 = outgauge_pack[17]
    display2 = outgauge_pack[18]
    optional_id = outgauge_pack[19]

    udp_gear = binascii.hexlify(gear).decode('utf-8')
	
    speed_mph = speed*2.23694
	
    if speed > 0:
	    print("%0.2f miles/hour %d rpm gear: %s" % (speed_mph, int(rpm),
		      transmission_gear(udp_gear)))
	    speed_string = str(speed_mph) + '\n'
	    arduino.write(speed_string.encode())
	    
    if arduino.inWaiting() > 0:
        print(arduino.read(arduino.inWaiting()).rstrip())
       