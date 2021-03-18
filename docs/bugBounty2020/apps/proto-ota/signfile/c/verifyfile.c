// VerifyFile
//
// C version of Ada ../ada/verifyfile.adb using same predefined public key
//
// This program uses WolfSSL/WolfCrypt implementation of Ed25519.
//
// WolfSSL must be installed with include files and libraries in standard
// locations.

#include <wolfssl/options.h>
#include <wolfssl/ssl.h>
#include <wolfssl/wolfcrypt/ed25519.h>
#include <stdio.h>

static const byte raw_pk[ED25519_PUB_KEY_SIZE] =
  {0xBA, 0xFB, 0xD4, 0xBB, 0x9F, 0x8E, 0xCE, 0xC1,
   0xEC, 0xE7, 0x42, 0xD7, 0xEA, 0x3B, 0x2E, 0xE2,
   0xE0, 0x16, 0xE3, 0x0F, 0x27, 0x0B, 0xAE, 0x74,
   0xB3, 0x0B, 0xED, 0xAC, 0x33, 0x47, 0x01, 0xFA};

int main (int argc, char *argv[])
{
  ed25519_key pk;
  int r;
  int signature_ok;
  FILE *fd;
  size_t fsize;
  size_t bytes_read;
  byte *sm;
  
  if (argc != 2)
    {
      printf ("usage: verifyfile signed_filename\n");
      return 0;
    }

  printf ("Trying to open %s\n", argv[1]);
  fd = fopen(argv[1], "r");
  if (fd == NULL)
    {
      if (errno == ENOENT)
	printf ("File does not exist\n");
      else
	printf ("Failed to open file with errno = %d\n", errno);
      return 0;
    }

  fseek (fd, 0L, SEEK_END);
  fsize = (size_t) ftell (fd);
  printf ("File size is %ld bytes\n", fsize);
  
  // Go back to the beginning of the file
  fseek (fd, 0L, SEEK_SET);

  if (fsize < ED25519_SIG_SIZE + 1)
    {
      printf ("File must be at least %d bytes long\n", ED25519_SIG_SIZE + 1);
      fclose (fd);
      return 0;
    }
  
  sm = (byte *)malloc (fsize);
  if (sm == NULL)
    {
      printf ("malloc() for sm failed\n");
      return 0;
    }
  
  for (int i = 0; i < fsize; i++)
    {
      sm[i] = 0;
    }
    
  bytes_read = fread (sm, 1, fsize, fd);
  if (bytes_read != fsize)
    {
      printf ("fread() failed\n");
      fclose (fd);
      return 0;
    }
  
  r = fclose (fd);
  if (r != 0)
    {
      printf ("Closing file failed with errno = %d\n", errno);
      return 0;
    }
    
  
  r = wc_ed25519_init (&pk);
  if (r != 0)
    {
      printf ("wc_ed25519_init() failed\n");
      return 0;
    }
  
  r = wc_ed25519_import_public (raw_pk, ED25519_PUB_KEY_SIZE, &pk);
  if (r != 0)
    {
      printf ("wc_ed25519_import_public() failed\n");
      return 0;
    }

  // sm points at the signature (64 bytes) followed directly by the message
  r = wc_ed25519_verify_msg(sm,                       // ptr to first byte of signature
			    ED25519_SIG_SIZE,         // size of signature

			    sm + ED25519_SIG_SIZE,    // ptr to first byte of message
			    fsize - ED25519_SIG_SIZE, // size of message

			    &signature_ok,            // Returned status
			    &pk);                     // public key
  if (r == 0 && signature_ok == 1)
    {
      printf ("Signature is OK\n");
    }
  else
    {
      printf ("Signature is NOT OK\n");
    }
  
  wc_ed25519_free (&pk);

  return 0;
}
