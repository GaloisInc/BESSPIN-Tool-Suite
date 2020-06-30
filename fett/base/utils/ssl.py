import os
import subprocess

def gen_cert(name, path, passw):
    key_name = os.path.join(path, "%s.key" % name)
    csr_name = os.path.join(path, "%s.csr" % name)
    crt_name = os.path.join(path, "%s.crt" % name)
    cur_dir = os.path.abspath(os.path.dirname(__file__))
    ca_path = os.path.join(cur_dir, "../../../apps/ssl/")
    ca_key = os.path.join(ca_path, "fettCA.key")
    ca_pem = os.path.join(ca_path, "fettCA.pem")

    subj = "/C=US/ST=OR/L=Portland/O=Galois, Inc/CN=%s" % name
    # Private Key
    subprocess.call(['openssl', 'genrsa', '-out', key_name, '2048'])
    # Certificate Signing Request
    subprocess.call(['openssl', 'req', '-new', '-key', key_name, '-out', csr_name,
    '-subj', subj])
    # Certificate
    process = subprocess.Popen(['openssl', 'x509', '-req', '-in', csr_name, '-CA', ca_pem,
        '-CAkey', ca_key, '-CAcreateserial', '-out', crt_name, '-days', '825',
         '-sha256', '-passin', 'stdin'],
        stdin = subprocess.PIPE,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        encoding = "utf8",
        shell=False
    )
    process.communicate("%s\n" % passw)