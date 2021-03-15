#!/usr/bin/env python

'''
Project: SSITH CyberPhysical Demonstrator
cyberphysical_demonstrator_led_manager.py
Author: Kristofer Dobelstein <kris.dobelstein@agilehardwarenwllc.com>
Date: 12/24/20202

Python 3.8.3
O/S: Windows 10

This Python file contains all of the functionality necessary to run a set of
WS2815 LED strings to represent dataflow as proposed by KAIA.

How it works:
1. LED strings are defined in a .csv file. Name, length, and behaviors for each
demonstrator state are defined.
2. This script opens the csv file, reads the headings, and the pulls values from
each row for each heading and creates an LEDstring object. 
3. This script assumes the main power supply is up and running then cycles
relays from off to on to power up the strings in a distributed fashion.
4. Once all strings are on, the script treats them as effectively self managing.
Each LEDstring is fed the current state of the demonstrator (e.g., "nominal"),
it then updates its pattern and color and dynamic state (e.g. lead pixel), and
the script packs up an array of tuples representing all connected LEDs and sends
it out to the Fadecandy boards.

Prerequisites:
1. Install Fadecandy on the PC at C:\Fadecandy. It can be found here:
https://github.com/scanlime/fadecandy
2. Fadecandy server JSON configuration file is updated with unique serial
numbers of Fadecandy boards. There is a nice tutorial on how to do this here:
https://github.com/scanlime/fadecandy/blob/master/doc/fc_server_config.md
3. LED strings are mapped to Fadecandy boards. Record serial number and channel.
4. Comma separated values file is built in the same order as the LED string to
Fadecandy map.

To do:
- Store csv 
- Package up into self-running thread
- Line wrap
'''

import os, psutil, subprocess
from pathlib import Path
import csv
import opc, time, numpy, pygame
import serial, serial.tools.list_ports_windows 

# set up a base file path so we can use relative paths for the Fadecandy
# server and the various configuration files
base_path = Path(__file__).parent

# Fadecandy
fadecandy_pid = None    # reserve a Fadecandy process ID variable
fadecandy_executable = "fcserver.exe"
fadecandy_json_cfg = "cyberphys_led_strings.json"

# LED string definitions csv
led_strings_csv = "led_strings_comprehensive_tuple_colors.csv"

# Relay interface and control parameters
# Relays here are Amazon ASIN B01CN7E0RQ
relay_usb_product_id = "29987" # note, this is a USB product ID, not a process ID
relay_baud = 9600
relay_on = b'\xA0\x01\x01\xA2'
relay_off = b'\xA0\x01\x00\xA1'

# LED network refresh time
regular_update_rate = 0.033  # seconds between updates
hack_update_rate = 0.0165   # seconds between updates

# Power management timing constants
system_time_delay_short = 1 # seconds
system_time_delay_warmup = 15 # seconds
relay_time_delay_blip = 0.1 # seconds
relay_time_delay_short = 0.25 # seconds
relay_time_delay_medium = 1 # seconds
relay_time_delay_long = 2 # seconds



# LEDstring class <start>-------------------------------------------------------
class LEDstring:
    def __init__(self, name, length, polarity,
                 nominal_pattern, nominal_pattern_color,
                 ssith_pattern, ssith_pattern_color,
                 brake_hack_pattern, brake_hack_pattern_color,
                 throttle_hack_pattern, throttle_hack_pattern_color,
                 steering_hack_pattern, steering_hack_pattern_color,
                 transmission_hack_pattern, transmission_hack_pattern_color,
                 all_off, all_off_color, all_on, all_on_color):
        # initialize with the following values
        self.name = name
        if (length >= 64):
            self.length = 64
            print('max value for LED string is 64')
        else:
            self.length = length+1  # passed from user, pixel 1 is first
                                            # active LED, so offset by 1
        self.polarity = polarity
        self.nominal_pattern = str(nominal_pattern)
        self.nominal_pattern_color = eval(nominal_pattern_color)
        self.ssith_pattern = str(ssith_pattern)
        self.ssith_pattern_color = eval(ssith_pattern_color)
        self.brake_hack_pattern = str(brake_hack_pattern)
        self.brake_hack_pattern_color = eval(brake_hack_pattern_color)
        self.throttle_hack_pattern = str(throttle_hack_pattern)
        self.throttle_hack_pattern_color = eval(throttle_hack_pattern_color)
        self.steering_hack_pattern = str(steering_hack_pattern)
        self.steering_hack_pattern_color = eval(steering_hack_pattern_color)
        self.transmission_hack_pattern = str(transmission_hack_pattern)
        self.transmission_hack_pattern_color = eval(transmission_hack_pattern_color)
        self.all_off = str(all_off)
        self.all_off_color = eval(all_off_color)
        self.all_on = str(all_on)
        self.all_on_color = eval(all_on_color)
        self._lead_pixel = 1 # start at one
        self._streamer_offset = 8
        self._current_pattern = "on"
        self._current_color = (255, 255, 255) # start at full brightness
        self._baseline_brightness = 0.35  # start at quarter
        self._pulse_strength = 1.0
        self._pulse_increase = True
        self.pixel_array = [self._current_color]*self.length
        self._offset_multiplier = 0
    
    def pad_array(self):
        '''
        Each Fadecandy board treats 8 strings of 64 pixels as a fixed array.        
        Each LED string starts at a fixed location: 1, 65, 129, 193, etc.
        array[0] doesn't turn an LED on...the first LED is at array[1] with the
        the last LED at [63]
        Adds a tuple of zeros to array[0] and pads the remaining locations
        '''
        if self.length == 64:
            #self.pixel_array = numpy.concatenate(((0,0,0), self.pixel_array))
            pass
        else:
            #print(64-self.length)
            array_padding = [ (0,0,0) ] * (64-self.length)
            self.pixel_array = numpy.concatenate((self.pixel_array, array_padding))

    def update_pattern(self, pattern_color, pattern_name, pattern_speed = "normal"):
        self.pixel_array = [tuple(int(self._baseline_brightness * x) for x in pattern_color)] * self.length  # reset the new frame to baseline color and intensity
        
        if (pattern_name == "off"):
            self.pixel_array = [(0,0,0)] * self.length

        if (pattern_name == "on"):
            self.pixel_array = [pattern_color] * self.length
        
        if (pattern_name == "ants"):
            
            self._offset_multiplier = 0
            while self._offset_multiplier < 8:
                try:
                    self.pixel_array[self._lead_pixel - (self._streamer_offset*self._offset_multiplier)] = pattern_color
                    self.pixel_array[self._lead_pixel - (self._streamer_offset*self._offset_multiplier) - 1] = tuple(numpy.array(pattern_color)*.8)
                    self.pixel_array[self._lead_pixel - (self._streamer_offset*self._offset_multiplier) - 2] = tuple(numpy.array(pattern_color)*.6)
                    self.pixel_array[self._lead_pixel - (self._streamer_offset*self._offset_multiplier) - 3] = tuple(numpy.array(pattern_color)*.4)                   
                except:
                    pass

                self._offset_multiplier += 1
                  
            if(self._offset_multiplier == 8): 
                self._offset_multiplier = 0
            
            self._lead_pixel += 1     
            if (self._lead_pixel >= self.length):
                self._lead_pixel = 1

        elif (pattern_name == "ants_reverse"):
            self._offset_multiplier = 0
            while self._offset_multiplier < 8:
                try:
                    self.pixel_array[self._lead_pixel - (self._streamer_offset*self._offset_multiplier)] = pattern_color
                    self.pixel_array[self._lead_pixel - (self._streamer_offset*self._offset_multiplier) + 1] = tuple(numpy.array(pattern_color)*.8)
                    self.pixel_array[self._lead_pixel - (self._streamer_offset*self._offset_multiplier) + 2] = tuple(numpy.array(pattern_color)*.6)
                    self.pixel_array[self._lead_pixel - (self._streamer_offset*self._offset_multiplier) + 3] = tuple(numpy.array(pattern_color)*.4)                   
                except:
                    pass
                self._offset_multiplier += 1
                  
            if(self._offset_multiplier == 8): 
                self._offset_multiplier = 0
            
            self._lead_pixel -= 1     
            if (self._lead_pixel <= 0):
                self._lead_pixel = self.length                

        elif (pattern_name == "pulse"):
            self.pixel_array = [tuple(numpy.array(pattern_color)*self._pulse_strength)] * self.length
            if (self._pulse_increase == True):
                self._pulse_strength += 0.05
            elif (self._pulse_increase == False):
                self._pulse_strength -= 0.05
            if (self._pulse_strength > 1.0):
                self._pulse_increase = False
            elif (self._pulse_strength <= 0.1):
                self._pulse_increase = True

        self.pad_array()    # set the array to the standard size

    def update_demonstrator_state(self, system_state):
        if system_state == "nominal":
            self._current_pattern = self.nominal_pattern
            self._current_color = self.nominal_pattern_color
        elif system_state == "ssith":
            self._current_pattern = self.ssith_pattern
            self._current_color = self.ssith_pattern_color
        elif system_state == "brake hack":
            self._current_pattern = self.brake_hack_pattern
            self._current_color = self.brake_hack_pattern_color
        elif system_state == "throttle hack":
            self._current_pattern = self.throttle_hack_pattern
            self._current_color = self.throttle_hack_pattern_color
        elif system_state == "steering hack":
            self._current_pattern = self.steering_hack_pattern
            self._current_color = self.steering_hack_pattern_color
        elif system_state == "transmission hack":
            self._current_pattern = self.transmission_hack_pattern
            self._current_color = self.transmission_hack_pattern_color
        elif system_state == "all off":
            self._current_pattern = self.all_off
            self._current_color = self.all_off_color
        elif system_state == "all on":
            self._current_pattern = self.all_on
            self._current_color = self.all_on_color

        self.update_pattern(self._current_color, self._current_pattern)
     
# LEDstring class <end>---------------------------------------------------------

'''
Appends the pixel_array from each LED string which contains a tuple for each LED
in the string and represents red, green, and blue intensities one large array.
'''
def pixels_for_opc(string_list):
    pixels = []
    for led_string in led_string_list:
        pixels = pixels + led_string.pixel_array

    return pixels

'''
Iterate through serial devices, find USB relays, and turn them on one by one
with a brief pause between each one to allow the power supply to remain stable.
'''    
def turn_on_relays(relay_pause = 4):

    # get all connected serial devices
    usb_devices = list(serial.tools.list_ports_windows.comports()) 

    for usb_device in usb_devices:
        if relay_usb_product_id in str(usb_device.pid):
            print("Turn on USB relay at " + str(usb_device.device))

            usb_relay = serial.Serial(port=usb_device.device,
                                      baudrate=relay_baud,
                                      timeout = 0.5)
            usb_relay.flushInput()
            usb_relay.write(relay_on)
            time.sleep(relay_pause)

'''
Iterate through serial devices, find USB relays, and turn them all off.
'''
def turn_off_relays():

    usb_devices = list(serial.tools.list_ports_windows.comports()) 

    for usb_device in usb_devices:
        if relay_usb_product_id in str(usb_device.pid):
            print("Turn off USB relay at " + str(usb_device.device))

            usb_relay = serial.Serial(port=usb_device.device,
                                      baudrate=relay_baud,
                                      timeout = 0.5)
            usb_relay.flushInput()
            usb_relay.write(relay_off)  

'''
Startup routine for the LED string network
1. All relays are set to off
2. All LEDs in each string are set off, which is each component set to (0,0,0)
3. "Off" is sent out to all Fadecandy boards which then transmit this data
4. Pause for a bit.
5. Set all LEDs in strings to on, which is each component set to (255,255,255)
6. Pause for a bit.
7. Turn on all relays with a brief pause between relays.
'''
def led_system_startup(startup_string_list):
    # turn off all relays
    turn_off_relays()

    # Set all LED strings to off
    for led_string in startup_string_list:
        led_string.update_demonstrator_state("all off")
    
    # Send the list of off tuples to the client
    client.put_pixels(pixels_for_opc(startup_string_list))
    
    # let the system stabilize
    time.sleep(system_time_delay_short)

    # turn on all LEDs
    # Command all LED strings to on
    for led_string in startup_string_list:
        led_string.update_demonstrator_state("all on")
    
    # Send the list of off tuples to the client    
    client.put_pixels(pixels_for_opc(startup_string_list)) 

    # rest for a moment
    time.sleep(system_time_delay_short)

    # turn on all relays and let LEDs warm up
    turn_on_relays(relay_time_delay_short)
    time.sleep(system_time_delay_warmup)

    # now quickly power cycle the system and let it run
    turn_off_relays()
    time.sleep(system_time_delay_short)
    turn_on_relays(relay_time_delay_short)

'''
The action starts here...
'''
# pygame for keyboard input
pygame.init()
pygame.display.set_mode(size=(300,200))

# check if Fadecandy server is running
for process in psutil.process_iter():
    try:
        if 'fcserver' in process.name():
            print("Fadecandy server is running as pid " + str(process.pid))
            fadecandy_pid = process.pid                 
    except:
        pass

# if it is running, shut it down and restart
if fadecandy_pid is not None:
    print("Shutting down Fadecandy and opening in known configuration.")
    os.kill(fadecandy_pid, 9)

# start Fadecandy in a known configuration
try:
    fadecandy_server = subprocess.Popen([(base_path / fadecandy_executable).resolve(), 
                                         (base_path / fadecandy_json_cfg).resolve()])
    print("Fadecandy server running as " + str(fadecandy_server.pid))
except:
    print("Could not start Fadecandy server.")   

# create the open pixel client
client = opc.Client('localhost:7890')    

# start with all relays off
turn_off_relays()

# Create the LEDstring objects from the csv file and store them in a list
led_string_list = []

with open((base_path / led_strings_csv).resolve(), 'r', newline='') as csv_file:
    reader = csv.DictReader(csv_file, delimiter=',')
    for row in reader:
        led_string_list.append(LEDstring(row["name"], 
                                int(row["length"]),
                                row["polarity"],
                                row["nominal pattern"],
                                row["nominal pattern color"],
                                row["ssith pattern"],
                                row["ssith pattern color"],
                                row["brake hack pattern"],
                                row["brake hack pattern color"],
                                row["throttle hack pattern"],
                                row["throttle hack pattern color"],
                                row["steering hack pattern"],
                                row["steering hack pattern color"],
                                row["transmission hack pattern"],
                                row["transmission hack pattern color"],
                                row["all off"],
                                row["all off color"],
                                row["all on"],
                                row["all on color"]))

# Sanity check, merely print out the names of the LEDstring objects
for led_string in led_string_list:
    print(str(led_string.name))

demonstrator_state = ["nominal", "ssith", "brake hack",
                         "throttle hack", "steering hack",
                         "transmission hack", "all off", "all on"]
demonstrator_state_index = 0

# power things up in a controlled, predictable manner
print("Powering up LED strings")
led_system_startup(led_string_list)

print(len(demonstrator_state))
print("Starting main loop in nominal state")

while(1):      
    for led_string in led_string_list:
        led_string.update_demonstrator_state(demonstrator_state[demonstrator_state_index])

    if "hack" in str(demonstrator_state[demonstrator_state_index]):        
        refresh_time = hack_update_rate   # go fast if hack in progress because scary
    else: refresh_time = regular_update_rate  # default timing        

    client.put_pixels(pixels_for_opc(led_string_list))
    client.put_pixels(pixels_for_opc(led_string_list))

    time.sleep(refresh_time)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                demonstrator_state_index += 1
                if demonstrator_state_index == len(demonstrator_state):
                    demonstrator_state_index = 0
                hack_target = demonstrator_state[demonstrator_state_index]
                print(hack_target) 
            if event.key == pygame.K_DOWN:
                demonstrator_state_index -= 1                
                if demonstrator_state_index <= -1:
                    demonstrator_state_index = len(demonstrator_state)-1
                    print(demonstrator_state_index)                    
                hack_target = demonstrator_state[demonstrator_state_index]
                print(hack_target)
            if event.key == pygame.K_q:
                print("Hard resetting LEDs")
                led_system_startup(led_string_list)
                demonstrator_state_index = 0
            if event.key == pygame.K_0:
                print("Turning off all relays")
                turn_off_relays()
            if event.key == pygame.K_1:
                print("Turn on all relays")
                turn_on_relays(relay_time_delay_blip)
