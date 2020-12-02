# Cyberphys C Library

This contains a C library for implementing the relevant communication and protocol
features for the SSITH Cyberphys demonstrator. This includes

* **CAN Bus** Can frame encoding/decoding.
* **J1939 Protocol** Multi packet communication using J1939 Broadcast Announcement Messaging (BAM). 

## Setup
The build files require `cmake 3.10+`. 
1. Make a directory to build in
```
$ mkdir build && cd build
```
2. Run cmake
```
$ cmake ..
```
Or, to build the cyberphys library for FreeRTOS (not yet implemented!),
```
cmake -D FREERTOS=ON ..
```
3. Run make
```
$ make
```
The examples should be in the `bin` subdirectory of the build directory.

## Examples
### Client / Server
In one terminal, launch the server example
```
$ ./server
```
In another,
```
$ ./client
```
The server receives a single can frame, as well as a multiple packet transmission. It 
reconstructs a buffer from the frames, and displays the message to the user.

### J1939 Utilities

An example to illustrate the J1939 utilities. Run,
```
./j1939_example
```
