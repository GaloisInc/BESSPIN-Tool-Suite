# BeamNG/Car Peripheral Support

 The BeamNG sim service is extended to communicate to the Smart Fortwo instrument cluster and throttle body. This is done by streaming a C struct over serial to a teensy board, which is responsible for converting the data contents into a collection of CAN packets. The BeamNG service is not responsible for sending the packets at a fixed rate, and the teensy board instills stricter timing to provide reliable operation of the cluster.

```
                  C struct                    CAN Packets
              (not fixed rate)           (50Hz, 20Hz Streams)
|BeamNG Service|----------->|Teensy Board|----------------->|Smart Fortwo Cluster|

```

## C Struct Contents

The C struct sent by the python based BeamNG sim service contains all possible data displayable by the cluster and throttle body. The contents are as follows:

| Value        | Type          | Description                         |
| ------------ | ------------- | ----------------------------------- |
| speed        | float         | mph                                 |
| fuel         | float         | [0,1] percentage                    |
| throttle     | float         | [0, 1] percentage                   |
| gear         | char          | {-1, 0, 1, 2, 3, 4, 5, 6} (R,N,1-6) |
| oil          | unsigned char | 0-1?                                |
| parkingbrake | unsigned char | {0, 1} (halfway is NOT used)        |
| highbeam     | unsigned char | 0-1?                                |
| headlights   | unsigned char | 0-2 (intensity)                     |                               |
| right_signal | unsigned char | bool (halfway is NOT used)          |
| left_signal  | unsigned char | bool (halfway is NOT used)          |
| esc_active   | unsigned char | bool                                |                               |
| abs_active   | unsigned char | bool                                |
| brake_lights | unsigned char | bool                               |

The python `struct` module is used to translate the python types to a C struct. The format string is `3fb4B6?`.

### Conversions

BeamNG Sim supplies an electrics sensor object. Several of these fields are transformed before being sent to the teensy, and others are left unmodified. The modified fields are:

| Transform Description              | Formula                         |
| ---------------------------------- | ------------------------------- |
| wheelspeed m/s -> mph              | (original value) * 2.2369       |
| parkingbrake {0, 0.5, 1} -> {0, 1} | (0, 1)[(original value) >= 0.5] |
| right_signal {0, 0.5, 1} -> {0, 1} | (0, 1)[(original value) >= 0.5] |
| left_signal {0, 0.5, 1} -> {0, 1}  | (0, 1)[(original value) >= 0.5] |

### Working Example

A small example can be created by attaching an arduino compatible processor to a machine capable of running the CyberPhys BeamNG service. The arduino code is provided, as well as the run command of the example service.

#### Arduino Program

```C
typedef struct {
  float wheelspeed_mph; /* mph */
  float fuel_percent; /* [0, 1] percentage */
  float throttle_percent; /* [0, 1] percentage */
  char gear_state; /* {-1, 0, 1, 2, 3, 4, 5, 6} (R,N,1-6) */
  unsigned char oil; /* {0, 1}? */
  unsigned char parkingbrake; /* {0, 1} (halfway is NOT used) */
  unsigned char highbeam; /* {0, 1}? */
  unsigned char headlights; /* 0-2 (intensity) */
  unsigned char right_signal; /* bool (halfway is NOT used) */
  unsigned char left_signal; /* bool (halfway is NOT used) */
  unsigned char esc_active; /* bool */
  unsigned char abs_active; /* bool */
  unsigned char brake_lights; /* bool */
} beamng_data;


beamng_data bngd;

void setup() {
  Serial.begin(115200);
  memset((void *)&bngd, 0, sizeof(beamng_data));
}

void loop() {
  if (Serial.available()) {
    /* read struct from serial */
    Serial.readBytes((char *)&bngd, sizeof(beamng_data));
  
    /* print results */
    Serial.print("Speed: ");
    Serial.print(bngd.wheelspeed_mph);
    Serial.println();
  }
}
```

#### Python Service

The script `can_com.py` launches a simple service to send data to a COM port of one's choosing. Run the command

```bash
python scripts/can_com.py -comport COMX -baud 115200 -loopback yes
```

Provided that the Arduino program is flashed on the uP, the script should report back the messages returned.
