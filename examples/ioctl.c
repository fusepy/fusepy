#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <inttypes.h>

#define M_IOWR _IOWR('M', 1, uint32_t)

int main(int argc,char *argv[]) {
    int fd;
    uint32_t data;
    if (argc != 3) {
        printf("Usage: %s value filename\n", argv[0]);
        return 1;
    }

    data = atoi(argv[1]);

    fd = open(argv[2], O_RDONLY);

    if (ioctl(fd, M_IOWR, &data) == -1)
        printf("M_IOWR failed: %s\n", strerror(errno));
    else {
        printf("M_IOWR successful, data = %u\n", data);
    }

    close(fd);
    return 0;
}
