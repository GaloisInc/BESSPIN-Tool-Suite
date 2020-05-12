#! /usr/bin/env python3
"""
--- fettED25519.py is a utility for generating key pairs/signing/verifying signature for OTA.
--- It uses ED25519 relying on a passcode.
--- This is not integrated in the tool.
--- Usage: fettED25519.py [-h] [-p GETPUBLICKEY] [-s SIGNFILE]
                      [-vf VERIFYSIGNATURE] [-k USEPUBLICKEY]

FETT-ED25519 (ED25519 utlity for FETT)

optional arguments:
  -h, --help            show this help message and exit
  -p GETPUBLICKEY, --getPublicKey GETPUBLICKEY
                        Dump out the public key to a file.
  -s SIGNFILE, --signFile SIGNFILE
                        Signs the input file.
  -vf VERIFYSIGNATURE, --verifySignature VERIFYSIGNATURE
                        verify the signature of a file.
  -k USEPUBLICKEY, --usePublicKey USEPUBLICKEY
                        Use input public key for verification instead of
                        passcode.
"""

def exitFett (exitCode=-1,exc=None,message=None):
    if (message):
        print(f"(Error)~  {message}")
    if (exc):
        print(f"(Error)~  <{exc.__class__.__name__}>: {exc}")
    if (exitCode == 0):
        print(f"(Info)~  End of fettED25519: <SUCCESS>")
    else:
        print(f"(Info)~  End of fettED25519: <FAILURE>")
    exit(exitCode)

def exitOnInterrupt (xSig,xFrame):
    signalNames = {2:'SIGINT', 15:'SIGTERM', 5:'SIGTRAP', 6:'SIGABRT'}
    if (xSig in signalNames):
        sigName = signalNames[xSig]
    else:
        sigName = f"signal#{xSig}"
    exitFett(message=f"Received <{sigName}>!")

try:
    import sys, os, signal, argparse
    import nacl.signing 
except Exception as exc:
    try:
        import sys
    except:
        exitFett (exc=exc)
    if (sys.executable.split('/')[1] != 'nix'):
        exitFett (message=f"Please run within a nix shell. [Run <nix-shell> in target-fett directory].")
    else:
        exitFett (exc=exc)
    
def main(xArgs):
    pass

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='FETT-ED25519 (ED25519 utlity for FETT)')
    xArgParser.add_argument ('-p', '--getPublicKey', help='Dump out the public key to a file.')
    xArgParser.add_argument ('-s', '--signFile', help='Signs the input file.')
    xArgParser.add_argument ('-vf', '--verifySignature', help='verify the signature of a file.')
    xArgParser.add_argument ('-k', '--usePublicKey', help='Use input public key for verification instead of passcode.')

    xArgs = xArgParser.parse_args()

    #Trapping the signals
    signalsToCatch = [signal.SIGINT, signal.SIGTERM, signal.SIGTRAP, signal.SIGABRT]
    for xSignal in signalsToCatch:
        signal.signal(xSignal,exitOnInterrupt)

    main(xArgs)