# HTTPS Server PoC with Nginx

## Nginx Overview

A minimal nginx server is desired to run on target platforms. Namely, it will serve the following features:

- the https webpage should be static
- the page opens another internet webpage through a link
- the page opens a text file
- the page opens an image
- the page receives a request and saves on the local filesystem
- the page links to another static page

## HTTPS Client Setup

HTTPS provides security with SSL or TLS. The protocol provides encryption between client and server as well as a form of authentication via handshaking.  For HTTPS, some decisions must be made

* What protocols to support (SSL v2.0, 3.0, TLS v1.0-1.2)
* An order of preference of ciphers (cipher suite negotiation)
* A certificate and a private key signed by a trusted Certificate Authority

Cloudflare has a recommended nginx configuration for [ssl protocol/ciphers](https://github.com/cloudflare/sslconfig/blob/master/conf), and Mozilla has a [cipher generator for nginx](https://ssl-config.mozilla.org/).

Create a CSR and private key using OpenSSL:

```
$ openssl genrsa -out key.pem 2048
$ openssl req -new -sha256 -key key.pem -out key.csr

# self-signed key
$ openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout key.key -out key.crt
```

Note that OpenSSL is recommended to be greater than version 1.0.1p.

### Nginx HTTPS Configuration Parameters

```nginx
server {
    listen 443 ssl;
    
	ssl_certificate /path/to/signed_cert_plus_intermediates;
    ssl_certificate_key /path/to/private_key;
    
    # faster connections for existing clients -- session resumption
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m; # share between nginx workers
    
    # cloudflare suggested configuration
    ssl_protocols               TLSv1 TLSv1.1 TLSv1.2 TLSv1.3;
	ssl_ciphers                 '[ECDHE-ECDSA-AES128-GCM-SHA256|ECDHE-ECDSA-CHACHA20-POLY1305|ECDHE-RSA-AES128-GCM-SHA256|ECDHE-RSA-CHACHA20-POLY1305]:ECDHE+AES128:RSA+AES128:ECDHE+AES256:RSA+AES256:ECDHE+3DES:RSA+3DES';
	ssl_prefer_server_ciphers   on;
}
```

