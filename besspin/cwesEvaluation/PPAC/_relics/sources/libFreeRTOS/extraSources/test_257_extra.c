/*
Test_257: Authentication Bypass by Spoofing
--- This file has extra parts for the test
-- This file's scope should be protected; otherwise, the test will fail (i.e. CWE exists)
*/

#include "../testsParameters.h"
#include "testgenFreeRTOS.h"

/* Data structures:
usersList: A list of users.
pwList: A list of passwords.
*/

#define USERS_LIST_LENGTH 3 //has to be >=2
#define SHA256_DIGEST_LENGTH 32

static char usersList[USERS_LIST_LENGTH][SUBJECT_CN_BUF_SIZE] = {"Yoda", "Jedi Order CLNT", "Baby Yoda"}; 

#if (TESTGEN_TEST_PART == 1) //use the sha256 hashes of the passwords
    static char pwList[USERS_LIST_LENGTH][2*SHA256_DIGEST_LENGTH+1] = {
        "e0dfbee7c045cf16c7628c4c66135cd725c17beb16909a8936611daf89867fb3", 
        "eeb7f2db116eda31c4a8a1bbbd4debdb90ed4f5211a7c10e280f474dd5bb44ff", 
        "364973cfe93db396bb20075f2a5d8969be07fc7920203ab7f238a2c5267f01e2"}; 
    extern int wc_Sha256Hash(const byte* data, word32 len, byte *out);
#elif (TESTGEN_TEST_PART == 2) //base64 Encoding
    static char pwList[USERS_LIST_LENGTH][PW_SIZE] = {
        "amVkaU1hc3RlcjEyMw==",
        "am95QFdvcmtfMTk5OQ==",
        "dGhlRm9yY2VJc1RoZUJlc3Q="}; 
    extern int Base64_Encode(const byte* in, word32 inLen, byte* out, word32* outLen);
#else //part 3 -- plainText
    static char pwList[USERS_LIST_LENGTH][PW_SIZE] = {"jediMaster123", "joy@Work_1999", "theForceIsTheBest"};
#endif


//functions declarations
uint8_t getServicePermission (const char * xActor, const char * inPW);

// This function receives an actor name and their password, and returns true/false to whether permission should be given
uint8_t getServicePermission (const char * xActor, const char * inPW) {
    onPrintf ("\t>>>>>> [getServicePermission]: Received request for <%s> with pw <%s>.\n",xActor,inPW);

    //process the password
    #if (TESTGEN_TEST_PART == 1) //get the sha256 value
        byte hash[SHA256_DIGEST_LENGTH];
        char xPW[2*SHA256_DIGEST_LENGTH+1]; //every byte is represented by 2 chars + null termination
        int funcReturn = wc_Sha256Hash((byte *) inPW, strlen(inPW), hash);
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [getServicePermission]: Error while obtaining the hash of <inPW>. [ret=%d]\n",funcReturn);
            exitTest (2);
            return uFALSE;
        }
        for(int i = 0; i < SHA256_DIGEST_LENGTH; i++) //loop to get the digestString
        {
            sprintf(xPW + (i * 2), "%02x", hash[i]);
        }
        xPW[2*SHA256_DIGEST_LENGTH] = 0;
    #elif (TESTGEN_TEST_PART == 2) //get the encoded value
        word32 xPWlen = 1 + 4*((2+strlen(inPW))/3); //+1 for the extra new line
        char * xPW = (char *) pvPortMalloc(xPWlen);
        if (xPW == NULL) {
            onPrintf ("<INVALID> [getServicePermission]: Malloc error while allocating <xPW>.\n");
            exitTest (2);
            return uFALSE;
        }
        int funcReturn = Base64_Encode((byte *) inPW, strlen(inPW), (byte *) xPW, &xPWlen);
        if (funcReturn != 0) {
            onPrintf ("<INVALID> [getServicePermission]: Error while obtaining the base64 of <inPW>. [ret=%d]\n",funcReturn);
            exitTest (2);
            return uFALSE;
        }
        xPW[xPWlen-1] = 0; //null terminating before the new line
    #else
        char * xPW = inPW;
    #endif

    //find the stored password
    onPrintf ("\t>>>>>> [getServicePermission]: Password was encoded to <%s>.\n",xPW);
    for (int i=0; i < USERS_LIST_LENGTH; i++) {
        if (!strcmp(xActor,usersList[i])) {
            onPrintf ("\t>>>>>> [getServicePermission]: Stored password for <%s> is <%s>.\n",usersList[i],pwList[i]);
            if (!strcmp(xPW,pwList[i])) {
                return uTRUE;
            } else {
                return uFALSE;
            }
        }
    }
    onPrintf ("\t>>>>>> [getServicePermission]: user <%s> not found.\n",xActor);
    return uFALSE;
}
