# Cyberphy hacking

## Hack OTA

```
# Compile dummy binary
cd hello-world; make clean; make linux; cd ..
./hack-ota.py --url http://10.88.88.11:5050 --platform Linux hello-world/hello-world-linux.elf
```

## Hack FreeRTOS

