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
    import sys, os, signal, argparse, getpass
    import nacl.signing, nacl.encoding, nacl.exceptions, hashlib
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
    # options sanity checks
    dumpPublicKey = (xArgs.getPublicKey is not None)
    doSignFile = (xArgs.signFile is not None)
    doVerifySignature = (xArgs.verifySignature is not None)
    usePublicKey = False
    if ((not dumpPublicKey) and (not doSignFile) and (not xArgs.verifySignature)):
        print("(info)~  Nothing to do.")
    
    if (xArgs.usePublicKey):
        if (dumpPublicKey):
            print("(Warning)~  Cannot use <-k,--usePublicKey> with <-p,--getPublicKey>. Ignoring <usePublicKey>.")
        elif (doSignFile):
            print("(Warning)~  Cannot use <-k,--usePublicKey> with <-s,--signFile>. Ignoring <usePublicKey>.")
        else:
            usePublicKey = True

    # Generate the key-pair
    if (dumpPublicKey or doSignFile or (doVerifySignature and (not usePublicKey))): #needs the private key --> generate
        print(f"(Info)~  Generating the key pair...")
        try:
            passcode = getpass.getpass(prompt='Passcode: ')
        except Exception as exc:
            exitFett(message="Failed to get the passcode.",exc=exc)
        try:
            passcodeEncoded = hashlib.sha256(passcode.encode('utf-8'))
        except Exception as exc:
            exitFett(message="Failed to obtain the sha256 of the passcode.",exc=exc)
        try: 
            signingKey = nacl.signing.SigningKey(passcodeEncoded.digest())
        except Exception as exc:
            exitFett(message="Failed to generate the ED25519 key pair.",exc=exc)
        print(f"(Info)~  EC25519 successfully generated from the provided passcode.")

        # Get the verify key (public key)
        publicKey = signingKey.verify_key

    # Dump public key
    if (dumpPublicKey):
        print(f"(Info)~  Dumping the public key...")
        keyLength = 64
        try:
            fKey = open(xArgs.getPublicKey,'w')
            hexString = str(publicKey.encode(encoder=nacl.encoding.HexEncoder),'utf-8')
            if (len(hexString) != keyLength):
                print(f"Public key length <{len(hexString)}> is not equal to <{keyLength}>.")
                raise
            listNibbles = ','.join([f"0x{hexString[2*i].upper()}{hexString[2*i+1].upper()}" for i in range(len(hexString)//2)])
            #listNibblesPretty = '\n'.join([listNibbles[40*i:(40*i)+40] for i in range(int(1+(keyLength-1)/16))]) #40 chars per line, i.e. 8 bytes.
            fKey.write(f"{listNibbles}\n")
            fKey.close()
        except Exception as exc:
            exitFett(message="Failed to dump the public key.",exc=exc)

        print(f"(Info)~  Public key saved in <{xArgs.getPublicKey}>")

    # Sign a file
    if (doSignFile):
        print(f"(Info)~  Signing the input file...")
        try:
            fFileToSign = open(xArgs.signFile,'rb')
            bytesToSign = fFileToSign.read()
            fFileToSign.close()
        except Exception as exc:
            exitFett(message="Failed to load the file to sign.",exc=exc)

        try:
            signedBytes = signingKey.sign(bytesToSign)
        except Exception as exc:
            exitFett(message="Failed to sign the file.",exc=exc)

        try:
            fSignedFile = open(f"{xArgs.signFile}.sig",'wb')
            fSignedFile.write(signedBytes)
            fSignedFile.close()
        except Exception as exc:
            exitFett(message="Failed to write the signed file.",exc=exc)

        print(f"(Info)~  File signed successfully.")

    # Verify signature
    if (doVerifySignature):
        print(f"(Info)~  Verifying the signature...")
        try:
            fFileToVerify = open(xArgs.verifySignature,'rb')
            bytesToVerify = fFileToVerify.read()
            fFileToVerify.close()
        except Exception as exc:
            exitFett(message="Failed to load the file to verify.",exc=exc)

        try:
            publicKey.verify(bytesToVerify)
        except nacl.exceptions.BadSignatureError:
            exitFett(message="verify: Bad Signature.")
        except Exception as exc:
            exitFett(message="Failed to verify the file to sign.",exc=exc)

        print(f"(Info)~  verify: Good signature!")

    exitFett(exitCode=0)

if __name__ == '__main__':
    # Reading the bash arguments
    xArgParser = argparse.ArgumentParser (description='FETT-ED25519 (ED25519 utlity for FETT)')
    xArgParser.add_argument ('-p', '--getPublicKey', help='Dumps out the public key to a file.')
    xArgParser.add_argument ('-s', '--signFile', help='Signs the input file.')
    xArgParser.add_argument ('-vf', '--verifySignature', help='verify the signature of a file.')
    xArgParser.add_argument ('-k', '--usePublicKey', help='Use input public key for verification instead of passcode.')

    xArgs = xArgParser.parse_args()

    #Trapping the signals
    signalsToCatch = [signal.SIGINT, signal.SIGTERM, signal.SIGTRAP, signal.SIGABRT]
    for xSignal in signalsToCatch:
        signal.signal(xSignal,exitOnInterrupt)

    main(xArgs)