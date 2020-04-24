# SignFile and VerifyFile prototypes

## Signfile

SignFile is a program that signs a given file with a given pass-phrase.
The latter is entered at the keyboard.

The pass-phrase is used to derive an Ed25519 private key that is used
with the NaCl crypto_sign operation to sign the file.

signfile filename

produces filename.sig

## Verifyfile

This program verifies a signed file, using a constant, known
Ed25519 public key, which is derived from a known pass-phrase.

## Test cases

* good.txt - example input message file, to be signed

* good.txt.sig - result of "signfile good.txt" using the known pass-phrase

* badsig.sig - A copy of good.txt.sig, but with one byte of the signature block modified

* badmsg.sig - A copy of good.txt.sig, but with one byte of the message block modified

* badboth.sig - A copy of good.txt.sig, but with one byte of both the signature and the message modified
