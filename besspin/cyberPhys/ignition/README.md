# Ignition User Guide

## Installation Guide
Ignition requires a Python 3.8 environment on Windows 10. 

### BeamNG.tech

Install BeamNG.tech using [these instructions](https://github.com/BeamNG/BeamNGpy).
Note that you will need to apply for a license, which may take a few days to obtain. Either
extract the downloaded zip file to `C:\BeamNG.tech` or wherever you specify 
in `cyberphyslib.config.BEAMNG_PATH`.

### BESSPIN `cyberphyslib`
Install python pip and setuptools. Navigate to `besspin/cyberPhys/cyberphyslib` and run
```
pip install -r requirements.txt
python setup.py install
```

### Sound Files
The infotainment stations play files matching `bensound-*.mp3` located at 
`cyberphyslib.config.RADIO_SOUND_DIR` (`C:\sound` by default).

## Configuration

The BESSPIN cyberphys demonstrator can be configured by modifying `cyberphyslib.config`.

For development, the network configuration may need to be changed. This can be done by modifying
`besspin/base/utils/setupEnv.json`. My local setup involves 3 machines:

* Infotainment Server on a Raspberry Pi
* Infotainment UI on a MacBook Pro
* Ignition on a Windows Gaming PC, with the following network changes 
```
--- a/besspin/base/utils/setupEnv.json
+++ b/besspin/base/utils/setupEnv.json
@@ -422,10 +422,10 @@
             "name" : "cyberPhysNodes",
             "type" : "dict",
             "val" : {
-                "AdminPc" : "10.88.88.1",
+                "AdminPc" : "<MY IP>",
                 "InfotainmentThinClient" : "<MY IP>",
                 "HackerKiosk" : "10.88.88.3",
-                "SimPc" : "10.88.88.4"
+                "SimPc" : "<MY IP>"
             }
         },
```

## Usage

### Ignition

Navigate to `besspin/cyberPhys/ignition` and run
```
python ignition.py
```

The ECU can be simulated by running (requires a Thrustmaster T150 Racing Wheel).
```
python ecusim.py
```

### CAN REPL
C&C packets can be sent to ignition using a CAN packet REPL
```
python canrepl.py -ip <MY_IP> -port 5002
```
An example command (from the `cyberphyslib.canlib` spec) is
```
can console> CMD_RESTART !I 0x30
```

### Unit Tests
Install pytest. Navigate to `besspin/cyberPhys/cyberphyslib` and run
```
pytest
```





