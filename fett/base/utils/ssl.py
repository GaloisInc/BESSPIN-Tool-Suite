import os
import subprocess
from fett.base.utils.misc import *

def gen_cert(name, key_path, cert_path):
    key_name = os.path.join(key_path, f"{name}.key")
    csr_name = os.path.join(key_path, f"{name}.csr")
    crt_name = os.path.join(cert_path, f"{name}.crt")
    ca_path = os.path.join(getSetting('repoDir'), 'apps', 'ssl')
    ca_key = os.path.join(ca_path, "fettCA.key")
    ca_pem = os.path.join(ca_path, "fettCA.pem")

    subj = f"/C=US/ST=OR/L=Portland/O=Galois, Inc/CN={name}"
    # Private Key
    shellCommand(['openssl', 'genrsa', '-out', key_name, '2048'])
    # Certificate Signing Request
    shellCommand(['openssl', 'req', '-new', '-key', key_name, '-out', csr_name,
    '-subj', subj])
    # Certificate
    shellCommand(['openssl', 'x509', '-req', '-in', csr_name, '-CA', ca_pem,
        '-CAkey', ca_key, '-CAcreateserial', '-out', crt_name, '-days', '825',
         '-sha256']
    )