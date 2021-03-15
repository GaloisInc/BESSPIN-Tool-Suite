# Introduction

The SSITH CyberPhysical Smart Fortwo will use a series of LED strings to visually represent the state of the demonstrator and the flow of data through an imaginary CAN bus topology. The attached filed, SSITH_SmartCarLEDpaths_103120.pdf, gives an overview of this idea.

# Hardware Notes
This setup includes 3D printed diffusers, dummy modules, LED strings, wiring, terminal blocks, power supply, relays, and capacitors. The Smart Fortwo will arrive with the 3D diffusers, LED strings, and dummy modules installed.

## Table of Critical Components
Component | Description | Vendor | SKU | Example (if helpful)
--------- | ----------- | ------ | --- | --------------------
Power Supply | MeanWell HRP-450-12 Power Supply, 12 volts, 37.5 amps | Digi-Key | [1866-2724-ND](https://www.digikey.com/en/products/detail/mean-well-usa-inc/HRP-450-12/7704311?s=N4IgTCBcDaILIFMCGA7A6ggNpgBACQCUAFAWgBYBWABhIEYIBdAXyA) | n/a
Terminal Blocks | High current, multi-circuit terminal block. Prototype utilizes 22-10 AWG terminal blocks sourced at local hardware retailers | Varies | Varies | [McMaster- Carr P/N 7527K46](https://www.mcmaster.com/7527K46/)
Spade terminals | 14-16 AWG, blue, various stud sizes | Typically available at local hardware retailers | Varies | [McMaster- Carr P/N 69145K72](https://www.mcmaster.com/69145K72/)
Ring terminals | 14-16 AWG, blue, various stud sizes | Typically available at local hardware retailers | Varies | [McMaster- Carr P/N 7113K23](https://www.mcmaster.com/7113K23/)
Spade terminals | 18-22 AWG, red, various stud sizes | Typically available at local hardware retailers | Varies | [McMaster- Carr P/N 69145K66](https://www.mcmaster.com/69145K66/)
Ring terminals | 18-22 AWG, red, various stud sizes | Typically available at local hardware retailers | Varies | [McMaster- Carr P/N 7113K35](https://www.mcmaster.com/7113K35/)
T-tap terminals | 14-16 AWG, blue | Typically available at local hardware retailers | Varies | [McMaster-Carr P/N 69515K24](https://www.mcmaster.com/69515K24/)
Quick-disconnect terminals | 14-16 AWG, blue | Typically available at local hardware retailers | Varies | [McMaster-Carr P/N 7243K22](https://www.mcmaster.com/7243K22/)
LED strings | WS2815 12 volt DC LED pixel strip light, 1 meter, 144 LEDs/meter, IP30, white PCB | BTF-Lighting | [WS28151M144LW30](https://www.btf-lighting.com/products/1-ws2815-dc12v-led-pixels-strip-light-dual-signal?variant=25774562345060) | n/a
Capacitors | Aluminum Electrolytic, >=1000 uF, >=25 volts DC | Varies | Varies | [Panasonic EEU-FR1E102](https://www.digikey.com/en/products/detail/panasonic-electronic-components/EEU-FR1E102/2433558)
Relays | USB controlled, 10 amp, 30 volt DC | Amazon | [B01CN7E0RQ](https://www.amazon.com/SMAKN%C2%AE-LCUS-1-module-intelligent-control/dp/B01CN7E0RQ/ref=sr_1_3?dchild=1&keywords=usb+relay&qid=1607538288&s=industrial&sr=1-3) | n/a
LED controllers | Fadecandy driver PCBA | Amazon | [B00K9M3VLE](https://www.amazon.com/Adafruit-FadeCandy-Dithering-USB-Controlled-NeoPixels/dp/B00K9M3VLE/ref=sr_1_3?dchild=1&keywords=fadecandy&qid=1608841551&sr=8-3) | n/a
USB cables | USB 2.0 Type A to Mini B (for Fadecandy boards) | Varies | Varies | [Amazon ASIN B00P0GI68M](https://www.amazon.com/UGREEN-Charging-Controller-Players-Receiver/dp/B00P0GI68M/ref=sr_1_3?dchild=1&keywords=usb+cable+mini+b&qid=1608841639&sr=8-3)
USB extension cables | USB Type A Male to USB Type A Female (for relays) | Varies | Varies | [Amazon ASIN B07RQRMGKB](https://www.amazon.com/AINOPE-Extension-MATERIAL-Transfer-Compatible/dp/B07RQRMGKB/ref=sr_1_1_sspa?dchild=1&keywords=usb+extension+cable&qid=1608841732&sr=8-1-spons&psc=1&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEyT1M5UjVTVkc2NjBLJmVuY3J5cHRlZElkPUEwMzc2MDAxMVlUOU01TTA2NVY1MSZlbmNyeXB0ZWRBZElkPUEwNTY4NTgxMVFRQ05FSEpISFpBRSZ3aWRnZXROYW1lPXNwX2F0ZiZhY3Rpb249Y2xpY2tSZWRpcmVjdCZkb05vdExvZ0NsaWNrPXRydWU=)

-- add JST hardware -- 

## LED Strings
The maximum length, in LED "pixels", of an LED string for Fadecandy is 63.

## Power and Distribution
Each LED draws a maximum of 15 mA when commanded at (255, 255, 255) or fully on at white. The LED installation in the car will need a power supply that can drive the network and not overheat. The following table shows power supply outputs in milliamps and how many LEDs and strings each one can drive.

Voltage | Current | Maximum LEDs per WS2815 datasheet | Maximum 63-LED strings
------- | ------- | --------------------------------- | ----------------------
12 | 10000 | 667 | 11
12 | 20000 | 1333 | 21
12 | 30000 | 2000 | 32
12 | 40000 | 2667 | 42
12 | 50000 | 3333 | 53
12 | 83000 | 5533 | 88
12 | 100000 | 6667 | 106

## Wiring
Each LED string will have a JST-style extension cable installed on it using standard 22 AWG "RGB" cable as show in the following image.
-- add a picture here --

# Software Prerequisites
Fadecandy must be installed on the PC running the LED network. It is here: https://github.com/scanlime/fadecandy.

# Python Example
The attached Python example runs up to 32 LED strings as it is loads Fadecandy with a JSON file with four unique serial numbered Fadecandy boards. The script has an introductory block that explains how it works.

# LED Network States
The following states are supported:
- nominal
- ssith
- brake hack
- throttle hack
- steering hack
- transmission hack
- all on at full brightness
- all off
