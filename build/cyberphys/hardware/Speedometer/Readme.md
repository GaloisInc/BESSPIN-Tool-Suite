# Overview

The speedometer system described here consists of BeamNG (the driving simulator), a Python bridge script, and a modified Smartcar speedometer assembly with an Arduino Micro inside running a sketch to drive the speedometer needle's stepper motor.

# BeamNG and Outgauge

BeamNG.drive (and BeamNG.research) have an [Outgauge channel](https://wiki.beamng.com/OutGauge). When enabled, the simulator broadcasts pertinent information regarding the state of the automobile including things like the selected gear, the speed, engine RPM, throttle position, and so on. Follow instructions in the aforementioned Outgauge channel link to enable this output channel.

# Bridge Script

The beamng_outgauge_to_arduino_speedometer.py script scans and identifies the COM ports on the computer for the Arduino Micro-based Smartcar speedometer, opens a serial port at the location of the Arduino Micro with a baud rate of 38400, listens to the Outgauge channel, unpacks the data structure, calculates miles per hour, encodes it as a utf-8 string with a new line character, and then transmits it to the speedometer over the serial port. It also listens for messages from the speedometer (e.g., "RIGHT" when the right button is pressed on the speedometer assembly).

# Smartcar Speedometer
## Hardware
The Smartcar speedometer assembly has an ATmega32u4 flashed as an Arduino Micro running on a custom printed circuit board. Pin assignments are called out in the sketch. A [Pololu DRV8834 Low-voltage Stepper Motor Driver Carrier](https://www.pololu.com/product/2134) drives the stepper motor clockwise or counterclockwise. The speedometer assembly runs completely from USB power.

A set of schematic (.sch) and printed circuit board layout (.brd) files are included. These files were created using Eagle Premium version 9.6.x.

Images of the modifications to the Smartcar Speedometer are included in the folder entitled Speedometer Modifications Photos.

## Arduino Sketch
The Smartcar Arduino sketch configures a serial connection at 38400, configures some pins for driving the stepper motor driver and some backlighting LEDs, enables the DRV8834 chip, configures it for quarter steps, and then resets the speedometer to zero miles per hour. It then listens for speed in miles per hour (as a string), converts it to a float, calculates the error between the target miles per hour and the current miles per hour, and rotates the stepper accordingly using a simple proportional control method. If the speed it receives is less than 0.1 miles per hour, the speedometer is set back to zero position.

## Some Operational Notes
Other speedometer operational notes:
* Speed is limited to 100 miles per hour. If the needle hits the limiter beyond 100 miles per hour, it has a tendency to get stuck there and needs to be manually swept back.
* The speedometer can be manually reset to zero miles per hour two ways:
  * By pressing the left button on the front of the speedometer assembly when miles per hour coming from BeamNG is zero. _Pressing the left button while the game is running does nothing._
  * Through the serial port if it receives the string "r\n".
* The right button on the speedometer assembly is free for use if necessary. When pressed, the Arduino transmits "RIGHT\n" over the serial port.
