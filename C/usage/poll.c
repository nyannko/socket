#include<stdio.h>
#include<string.h>
#include<poll.h>

int main(void) {

    int fd = 0;
    char str [11];
    int res;

    /* params for poll */
    struct pollfd fds[1];
    int timeout;

    while(1) {
        fds[0].fd = fd;
        fds[0].events = 0;
        fds[0].events |= POLLIN;

        /* set timeout value*/
        timeout = 5000;

        res = poll(fds, 1, timeout);

        if(res == -1) {
            perror("poll()");
        }
        else if (res == 0) {
            printf("res = %d", res);
            printf("    timeout\n");
        } else {
            printf("res = %d", res);
            memset((void*) str, 0 ,11); /*string.h, read 11 bytes*/
            int num = read(fd, (void*) str, 11);
            printf("    The number of bytes is: %d\n", num);

            if(num >= 0) {
                printf("str = %s ", str);
            }
        }
    }

    return 0;
}
