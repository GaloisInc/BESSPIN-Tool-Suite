#include "mbedtls/config.h"
#include "mbedtls/platform.h"
#include "mbedtls/sha256.h"

#include <stdio.h>
#include <string.h>

#include "tweetnacl.h"
#include "d.h"

int main ()
{
  char passphrase[64] = { 0 };

  const unsigned char m[64] =
    {0x55, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa,
     0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa,
     0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa,
     0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa,
     0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa,
     0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa,
     0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa,
     0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa, 0xaa};
  unsigned char sm[64 + crypto_sign_BYTES];
  unsigned char m2[64 + crypto_sign_BYTES];
  unsigned long long smlen;
  unsigned long long m2len;

  unsigned char d[32];
  int r;
  unsigned char pk1[crypto_sign_PUBLICKEYBYTES];
  unsigned char sk1[crypto_sign_SECRETKEYBYTES];
  unsigned char pk2[crypto_sign_PUBLICKEYBYTES];
  unsigned char sk2[crypto_sign_SECRETKEYBYTES];

  printf ("What's the password: ");
  r = scanf ("%63s", passphrase);
  printf ("scanf() returns %d\n", r);
  printf ("strlen(passphrase) is %ld\n", strlen(passphrase));

  r = mbedtls_sha256_ret ((unsigned char *) passphrase, strlen(passphrase), d, 0);
  printf ("SHA256 returns %d\n", r);
  printf ("SHA256 of passphrase is\n");
  for (int i = 0; i < 32; i++)
    {
      printf ("%2x ", d[i]);
    }
  printf ("\n");

  // Now derive an Ed25519 keypair from d
  crypto_sign_keypair_from_bytes (d, pk1, sk1);
  dh ("PK1 is ", pk1, crypto_sign_PUBLICKEYBYTES);
  dh ("SK1 is ", sk1, crypto_sign_SECRETKEYBYTES);

  // Modify d and derive a second, different keypair
  d[1] = d[1] + 1;
  crypto_sign_keypair_from_bytes (d, pk2, sk2);

  printf ("Case 1 - correct keys and message\n");
  r = crypto_sign (sm, &smlen, m, 64, sk1);
  printf ("crypto_sign returns %d\n", r);
  dh ("SM is ", sm, 64 + crypto_sign_BYTES);

  r = crypto_sign_open (m2, &m2len, sm, 64 + crypto_sign_BYTES, pk1);
  if (r == 0) {
    printf ("Signature OK\n");
    printf ("m2len is %lld\n", m2len);
    dh ("M2 is ", m2, m2len);
  } else {
    printf ("Signature NOT OK\n");
  }

  printf ("Case 2 - same message but wrong public key\n");
  r = crypto_sign_open (m2, &m2len, sm, 64 + crypto_sign_BYTES, pk2);
  if (r == 0) {
    printf ("Signature OK\n");
    printf ("m2len is %lld\n", m2len);
    dh ("M2 is ", m2, m2len);
  } else {
    printf ("Signature NOT OK\n");
  }

  printf ("Case 3 - same message, correct public key, but wrong private key\n");
  r = crypto_sign (sm, &smlen, m, 64, sk2);
  printf ("crypto_sign returns %d\n", r);
  r = crypto_sign_open (m2, &m2len, sm, 64 + crypto_sign_BYTES, pk1);
  if (r == 0) {
    printf ("Signature OK\n");
    printf ("m2len is %lld\n", m2len);
    dh ("M2 is ", m2, m2len);
  } else {
    printf ("Signature NOT OK\n");
  }

  printf ("Case 4 - correct keys, but message corrupted\n");
  r = crypto_sign (sm, &smlen, m, 64, sk1);
  printf ("crypto_sign returns %d\n", r);

  // Corrupt SM data in some way
  sm[65] = sm[65] - 1;

  r = crypto_sign_open (m2, &m2len, sm, 64 + crypto_sign_BYTES, pk1);
  if (r == 0) {
    printf ("Signature OK\n");
    printf ("m2len is %lld\n", m2len);
    dh ("M2 is ", m2, m2len);
  } else {
    printf ("Signature NOT OK\n");
  }

  printf ("Case 5 - correct keys, but signature corrupted\n");
  r = crypto_sign (sm, &smlen, m, 64, sk1);
  printf ("crypto_sign returns %d\n", r);

  // Corrupt SM signature in some way
  sm[0] = sm[0] - 1;

  r = crypto_sign_open (m2, &m2len, sm, 64 + crypto_sign_BYTES, pk1);
  if (r == 0) {
    printf ("Signature OK\n");
    printf ("m2len is %lld\n", m2len);
    dh ("M2 is ", m2, m2len);
  } else {
    printf ("Signature NOT OK\n");
  }

  return 0;
}
