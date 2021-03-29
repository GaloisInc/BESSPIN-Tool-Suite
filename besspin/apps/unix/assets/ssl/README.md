This directory contains the root CA cert for generating BESSPIN app
certificates.

The **gencert** script can be used to generate a test certificate, but
is not called by BESSPIN directly.  The code used to generate certificates
for BESSPIN builds is in `besspin/base/utils/ssl.py`