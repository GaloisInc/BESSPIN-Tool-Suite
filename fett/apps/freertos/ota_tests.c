//  Tests for Ed25519 Signature Verification using WolfSSL in FreeRTOS

#include "fettFreeRTOS.h"
#include "ota_tests.h"

static const byte raw_pk[ED25519_KEY_SIZE] =
  {0xBA, 0xFB, 0xD4, 0xBB, 0x9F, 0x8E, 0xCE, 0xC1,
   0xEC, 0xE7, 0x42, 0xD7, 0xEA, 0x3B, 0x2E, 0xE2,
   0xE0, 0x16, 0xE3, 0x0F, 0x27, 0x0B, 0xAE, 0x74,
   0xB3, 0x0B, 0xED, 0xAC, 0x33, 0x47, 0x01, 0xFA};

#define GOOD_SIG_SIZE 70
static const byte good_signature[GOOD_SIG_SIZE] = {
  0xac, 0xa3, 0x99, 0x24, 0x9d, 0xe4, 0x94, 0x20, 0x0f, 0x11, 0xc4, 0xf2,
  0x52, 0x3e, 0xef, 0x90, 0xc3, 0x9e, 0x1f, 0xdb, 0xe3, 0xe5, 0x32, 0x33,
  0x67, 0x23, 0x00, 0xa2, 0xd3, 0x1d, 0xbf, 0x41, 0x4c, 0xcb, 0x2e, 0xb3,
  0x2b, 0xf6, 0x28, 0xef, 0x01, 0x48, 0xe4, 0x81, 0xca, 0x3b, 0xb0, 0xde,
  0x74, 0x07, 0x12, 0xc2, 0xf6, 0x64, 0x5b, 0x34, 0x5b, 0xe9, 0x85, 0x8b,
  0x32, 0xcb, 0x0f, 0x01, 0x68, 0x65, 0x6c, 0x6c, 0x6f, 0x0a
};
unsigned int good_txt_sig_len = 70;

void test_ed25519_verify(void)
{
  ed25519_key pk;
  int r;
  int signature_ok;

  r = wc_ed25519_init (&pk);
  if (r != 0)
    {
      fettPrintf ("wc_ed25519_init() failed\n");
      return;
    }

  r = wc_ed25519_import_public (raw_pk, ED25519_KEY_SIZE, &pk);
  if (r != 0)
    {
      fettPrintf ("wc_ed25519_import_public() failed\n");
      return;
    }

  // TEST CASE 1 - GOOD SIGNATURE

  fettPrintf ("Test case 1 - expected good signature\n");

  // sm points at the signature (64 bytes) followed directly by the message
  r = wc_ed25519_verify_msg((byte *) good_signature,  // ptr to first byte of signature
                            ED25519_SIG_SIZE,         // size of signature

                            good_signature + ED25519_SIG_SIZE, // ptr to first byte of message
                            GOOD_SIG_SIZE - ED25519_SIG_SIZE,  // size of message

                            &signature_ok,            // Returned status
                            &pk);                     // public key
  if (r == 0 && signature_ok == 1)
    {
      fettPrintf ("Signature is OK\n");
    }
  else
    {
      fettPrintf ("Signature is NOT OK\n");
    }

  wc_ed25519_free (&pk);
}
