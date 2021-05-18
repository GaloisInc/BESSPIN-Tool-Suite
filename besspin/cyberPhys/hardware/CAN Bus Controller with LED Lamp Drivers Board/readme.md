# Introduction
The CAN Bus Controller with LED Lamp Drivers Board (REV 1) is a Teensy 3.6-based solution with a variety of embedded circuitry and system interfaces including:
- UART
- I2C x 3
- CAN bus
- Analog sensing
- Digital I/O
- PWM outputs

Schematic and Board were created using Eagle 9.6.2 Premium. The following design artifacts are included in this repository:
- Schematic and Board Layout files
- Bill of Materials
- Gerber files

# 12 Volt Power Input Option
There is a 12 volt power input option in CN2. Pin #1 is +12 volts. Pin #2 is ground. Read the following sections for more information on how it works. Do not exceed 30 volts on this input connector.

## Teensy 3.6 Power
The Teensy 3.6 can be powered via the USB port _or_ the 12 volt input (CN2). __If using the 12 volt input and the Teensy 3.6 is connected to USB, Jumper J1 should be open circuit.__

## Downstream Device Power
This board is typically connected in some fashion to a downstream automotive device such as an instrument cluster or a gear shifter assembly. When this is the case, wiring can be kept tidy by running power through this board from CN2 to CN1 and/or CN4. __If using the 12 volt input and the Teensy 3.6 is connected to USB, Jumper J1 should be open circuit.__

# CAN Bus
There is a Texas Instruments automotive grade TCAN332 transceiver (U2) with on-board termination (R3). It runs from +3.3V, which makes it a good match for the Teensy 3.6. More information is here: https://www.ti.com/product/TCAN332. Note that in this design, the CAN bus is interfaced to the alternative pins on the Teensy 3.6.

# LED Lamp Drivers
There are four LED lamp driver interfaces across CN9 and CN10 labeled LED1, LED2, LED3, and LED4. Practically speaking, each one of these outputs is merely 12 volts switched on or off to the LED's anode through a smart high side switch (https://www.infineon.com/cms/en/product/power/smart-low-side-high-side-switches/high-side-switches/classic-profet-12v-automotive-smart-high-side-switch/bts5014sda/). Given this, these outputs can also be used to power a 12 volt downstream device. _Do not exceed a 1 amp per LED channel._

## LED Lamp Driver Alternate Control
The LED Lamp Drivers can be controlled through CN8. A positive signal applied to CTRL_LED_BULB_# will activate the associated smart switch. _In order to use the alternate control input, R12, R13, R14, and R15 must be removed from the printed circuit board assembly._

If using a VCU118-based GPIO for this control interface, MOSFETs Q2, Q3, Q4, and Q5 should be replaced with __Infineon BSR802NL6327HTSA1__ to ensure compatibility with its positive output signal.
