# Introduction
The CAN Bus Controller Board (REV 1) is a Teensy 3.2-based solution with a variety of embedded circuitry and system interfaces including:
- UART
- I2C
- CAN bus
- Analog sensing
- Digital I/O
- PWM outputs

Schematic and Board were created using Eagle 9.6.2 Premium. The following design artifacts are included in this repository:
- Schematic and Board Layout files
- Bill of Materials
- Gerber files

# 12 Volt Power Input Option
There is a 12 volt power input option in CN2. Read the following sections for more information on how it works. Do not exceed 30 volts on this input connector.

## Teensy 3.2 Power
The Teensy 3.2 can be powered via the USB port _or_ the 12 volt input (CN2). __If using the 12 volt input and the Teensy 3.2 is connected to USB, Jumper J1 should be open circuit.__

## Downstream Device Power
This board is typically connected in some fashion to a downstream automotive device such as an instrument cluster or a gear shifter assembly. When this is the case, wiring can be kept tidy by running power through this board from CN2 to CN1 and/or CN4. __If using the 12 volt input and the Teensy 3.2 is connected to USB, Jumper J1 should be open circuit.__

# CAN Bus
There is a Texas Instruments automotive grade TCAN332 transceiver (U2) with on-board termination (R3). It runs from +3.3V, which makes it a good match for the Teensy 3.2. More information is here: https://www.ti.com/product/TCAN332
