# Cyberphy hacking

## Hack OTA

```
# Compile dummy binary
cd hello-world; make clean; make linux; cd ..
./hack-ota.py --url http://10.88.88.11:5050 --platform Linux hello-world/hello-world-linux.elf
```

## Hack FreeRTOS

**TODO**

```
openocd --command "set _CHIPNAME riscv_1; gdb_port 3004; telnet_port 3005; adapter usb location 1-4.4.4.4" -f besspin/target/utils/openocd_vcu118.cfg

minicom -D /dev/ttyUSB10 -b 115200

```
