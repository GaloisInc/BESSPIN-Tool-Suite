# Prototypes for Over-the-Air (OTA) services

This directory contains prototypes and experimental work-in-progress
for the OTA demo application.

## Sub-directories

sign - prototype private key derivation and signing/verification programs.

sign/ada - reference implemenation in Ada for MacOS or Linux. Builds using GNAT Community 2019 or better.

sign/c - reference implementation in C using mbedtls and tweetnacl libraries. Builds using the tool-suite nix-shell environment on Linux.

signfile/ada/signfile.adb - Host-based program to sign a given file with a key derived from a pass-phrase.

signfile/ada/verifyfile.adb - Host-based program to verify the signature of a given file, using a known public key, derived from a known pass-phrase.

## Dependencies

The C version for Linux needs mbedtls installed and built in the same directory as SSITH-FETT-Target

The Ada version needs the SPARKNaCl library installed somewhere - see the GPR file.
