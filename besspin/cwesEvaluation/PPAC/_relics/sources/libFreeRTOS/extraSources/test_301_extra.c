/*
Test_301: Reflection Attack in an Authentication Protocol
--- This file has extra parts for the test
-- This file's scope should be protected; otherwise, the test will fail (i.e. CWE exists)
*/

#include "../testsParameters.h"
#include "testgenFreeRTOS.h"
#include "dhParams.h" //the key

/* Data structures:

*/

void printKey (const char * keyName, const byte * key, const word32 keySz);
void loadDHparams (void);
void freeDHparams (void);
static DhKey globalKey;
static RNG rng;

#if (TESTGEN_TEST_PART == 1) || (TESTGEN_TEST_PART == 2)
    void genDHKeyPair (byte * pubKey, word32 * pubSz, byte * privKey, word32 * privSz, char iConn);
    void genDHSecret (const byte * privKey, word32 privSz, const byte * pubHost, word32 pubHostSz, char iConn); 
#elif (TESTGEN_TEST_PART == 3)
    void respondToDHChallenge (const byte * chalKey, word32 chalSz, byte * respKey, word32 * respSz, char iConn);
    void createDHChallenge (byte * chalKey, word32 * chalSz, char iConn);
    uint8_t getServicePermission (const byte * chalKey, word32 chalSz, const byte * recvAns, word32 recvAnsSz, char iConn);
    extern int GeneratePublic(DhKey* key, const byte* priv, word32 privSz, byte* pub, word32* pubSz);
    extern int GeneratePrivate(DhKey* key, RNG* rng, byte* priv, word32* privSz);
#endif

#if (TESTGEN_TEST_PART == 2)
    byte respTarget[KEY_SIZE], privTarget[KEY_SIZE];
    word32 respTargetSz, privTargetSz;
#endif


//Initialize DH and load the DHparams file
void loadDHparams (void) {
    //from wolfcrypt/tests/test.c:dh_test && wolfssl documentation-section:10.5.2
        //tmp --> dhParams_pem
        //bytes --> dhParams_pem_len

    onPrintf ("[loadDHparams]: Initializing Diffie-Hellman parameters.\n");
    int funcReturn;

    //Obtain the key
    wc_InitDhKey(&globalKey);
    word32 idx = 0;
    funcReturn = wc_DhKeyDecode(dhParams_der, &idx, &globalKey, dhParams_der_len);
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [loadDHparams]: Error while decoding the key. [ret=%d]\n",funcReturn);
        prEXIT(2);
    }

    funcReturn = wc_InitRng(&rng);
    if (funcReturn != 0) {
        onPrintf ("<INVALID> [loadDHparams]: Error while initializing the RNG. [ret=%d]\n",funcReturn);
        prEXIT(2);
    }   

    #if (TESTGEN_TEST_PART == 2) //same key-pair
        genDHKeyPair (respTarget, &respTargetSz, privTarget, &privTargetSz, 'S');
    #endif

    onPrintf ("[loadDHparams]: Initialization complete.\n");
    return;
}

//Free DH
void freeDHparams (void) {
    wc_FreeDhKey(&globalKey);
    wc_FreeRng(&rng);
    return;
}

void printKey (const char * keyName, const byte * key, const word32 keySz) {
    char strKey[2*keySz+1]; //every byte is represented by 2 chars + null termination

    for(word32 i = 0; i < keySz; i++)
    {
        sprintf(strKey + (i * 2), "%02x", key[i]);
    }
    strKey[2*keySz] = 0;

    onPrintf ("<%s>:<%s>\n",strKey,keyName);

    return;
}

#if (TESTGEN_TEST_PART == 1) || (TESTGEN_TEST_PART == 2)
    //generate a key-pair
    void genDHKeyPair (byte * pubKey, word32 * pubSz, byte * privKey, word32 * privSz, char iConn) {
        onPrintf ("[genDHKeyPair-%c]: Generating keys.\n",iConn);
        int funcReturn;

        // generate a private key, and the partial DH key based on the initial public parameters in dhParams
        funcReturn = wc_DhGenerateKeyPair(&globalKey, &rng, privKey, privSz, pubKey, pubSz);
        if (funcReturn < 0) {
            onPrintf ("<INVALID> [genDHKeyPair-%c]: Error while generating key pair. [ret=%d]\n",iConn,funcReturn);
            prEXIT(2);
        }   

        onPrintf ("[genDHKeyPair-%c]: Generating key pair is complete. [privSz=%d, pubSz=%d]\n",iConn, *privSz, *pubSz);
        char keyName[] = "TARGET-GEN-X-PUB-KEY";
        sprintf (keyName,"TARGET-GEN-%c-PUB-KEY",iConn);
        printKey (keyName,pubKey,*pubSz);

        return;

    }

    // Gen key pair and secret from a public key + Dhparams
    void genDHSecret (const byte * privKey, word32 privSz, const byte * pubHost, word32 pubHostSz, char iConn) {
        onPrintf ("[genDHSecret-%c]: Generating Shared secret.\n",iConn);
        int funcReturn;

        byte agree[KEY_SIZE];
        word32 agreeSz;

        funcReturn = wc_DhAgree(&globalKey, agree, &agreeSz, privKey, privSz, pubHost, pubHostSz);
        if (funcReturn < 0) {
            onPrintf ("<INVALID> [genDHSecret-%c]: Error while generating shared secret. [ret=%d]\n",iConn,funcReturn);
            prEXIT(2);
        }   

        onPrintf ("[genDHSecret-%c]: Generating shared secret complete. [agreeSz=%d]\n",iConn,agreeSz);
        char keyName[] = "TARGET-GEN-X-SECRET";
        sprintf (keyName,"TARGET-GEN-%c-SECRET",iConn); 
        printKey (keyName,agree,agreeSz);

        return;
    }
#elif (TESTGEN_TEST_PART == 3)
    //completes a challenge
    void respondToDHChallenge (const byte * chalKey, word32 chalSz, byte * respKey, word32 * respSz, char iConn) {
        onPrintf ("[respondToDHChallenge-%c]: Generating the challenge response.\n",iConn);
        int funcReturn;

        // generate partial DH key based on the given challenge and the initial public parameters in dhParams
        funcReturn = GeneratePublic(&globalKey, chalKey, chalSz, respKey, respSz);
        if (funcReturn < 0) {
            onPrintf ("<INVALID> [respondToDHChallenge-%c]: Error while generating the challenge response. [ret=%d]\n",iConn,funcReturn);
            prEXIT(2);
        }  

        onPrintf ("[respondToDHChallenge-%c]: Generating the challenge response is complete. [respSz=%d]\n",iConn, *respSz);
        char keyName[] = "TARGET-GEN-X-RESPONSE";
        sprintf (keyName,"TARGET-GEN-%c-RESPONSE",iConn);
        printKey (keyName,respKey,*respSz);

        return; 
    }

    //creates a challenge
    void createDHChallenge (byte * chalKey, word32 * chalSz, char iConn) {
        onPrintf ("[createDHChallenge-%c]: Creating a challenge.\n",iConn);
        int funcReturn;

        // generate a key to challenge
        funcReturn = GeneratePrivate(&globalKey, &rng, chalKey, chalSz);
        if (funcReturn < 0) {
            onPrintf ("<INVALID> [createDHChallenge-%c]: Error while generating a challenge key. [ret=%d]\n",iConn,funcReturn);
            prEXIT(2);
        }  

        onPrintf ("[createDHChallenge-%c]: Creating a challenge is complete. [chalSz=%d]\n",iConn, *chalSz);
        char keyName[] = "TARGET-GEN-X-CHALLENGE";
        sprintf (keyName,"TARGET-GEN-%c-CHALLENGE",iConn);
        printKey (keyName,chalKey,*chalSz);

        return;        
    }

    uint8_t getServicePermission (const byte * chalKey, word32 chalSz, const byte * recvAns, word32 recvAnsSz, char iConn) {
        onPrintf ("\t>>>>>> [getServicePermission-%c]: Received request.\n",iConn);
        int funcReturn;

        // --------- Print the Challenge response -------------
        byte ansKey[KEY_SIZE];
        word32 ansSz;
        funcReturn = GeneratePublic(&globalKey, chalKey, chalSz, ansKey, &ansSz);
        if (funcReturn < 0) {
            onPrintf ("<INVALID> [getServicePermission-%c]: Error while generating the challenge answer. [ret=%d]\n",iConn,funcReturn);
            exitTest(2);
            return uFALSE;
        }  

        onPrintf ("\t>>>>>> [getServicePermission-%c]: Generating the challenge answer is complete. [ansSz=%d]\n",iConn, ansSz);
        char keyName[] = "TARGET-GEN-X-ANSWER";
        sprintf (keyName,"TARGET-GEN-%c-ANSWER",iConn);
        printKey (keyName,ansKey,ansSz);

        onPrintf ("\t>>>>>> [getServicePermission-%c]: Comparing the answer to the received response...\n",iConn);
        if (ansSz != recvAnsSz) {
            onPrintf ("\t>>>>>> [getServicePermission-%c]: Sizes do not match!\n",iConn);
            return uFALSE;
        }

        for (word32 iByte=0; iByte<ansSz; iByte++) {
            if (recvAns[iByte] != ansKey[iByte]) {
                onPrintf ("\t>>>>>> [getServicePermission-%c]: Mismatch in the <%d>th byte.\n",iConn,iByte);
                return uFALSE;
            }
        }
        onPrintf ("\t>>>>>> [getServicePermission-%c]: No mismatch found in <%d bytes>.\n",iConn,ansSz);
        return uTRUE;
    }

#endif //parts functions
