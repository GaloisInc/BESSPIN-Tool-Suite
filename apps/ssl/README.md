This directory contains the root CA cert for generating FETT app
certificates.

The **gencert** script can be used to generate a test certificate, but
is not called by FETT directly.  The code used to generate certificates
for FETT builds is in `fett/base/utils/ssl.py`