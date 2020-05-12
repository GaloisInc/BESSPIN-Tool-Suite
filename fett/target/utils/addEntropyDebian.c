#include <linux/random.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>
#include <stdio.h>
#include <sys/ioctl.h>

#define BUF_SIZE 128

/* WARNING - this struct must match random.h's struct rand_pool_info */
typedef struct {
    int bit_count;               /* number of bits of entropy in data */
    int byte_count;              /* number of bytes of data in array */
    char buf[BUF_SIZE];
} entropy_t;

int main () {
    int randFd = open("/dev/urandom",O_RDONLY);
    entropy_t entropyData;
    entropyData.bit_count = 8*BUF_SIZE; //This should be ignored by /dev/urandom if too high
    entropyData.byte_count = BUF_SIZE;

    int ret = ioctl(randFd, RNDADDENTROPY, entropyData);
    if (ret != 0) {
        printf ("<INVALID> Failed to add to the entropy pool (ERRNO.name=%s)\n",strerror(errno));
    }

    close(randFd);
}