#include<stdio.h>
#include<string.h>
#include<sys/select.h>

int main(void) {

    int fd = 0;
    char str [11];
    int res;

    /* params for select */
    fd_set readfd;
    struct timeval timeout;

    while(1) {
        FD_ZERO(&readfd);
        FD_SET(fd, &readfd);

        /* set timeout value*/
        timeout.tv_sec = 5;
        timeout.tv_usec = 0;

        res = select(8, &readfd, NULL, NULL, &timeout);

        if(res == -1) {
            perror("select()");
        } else if (res == 0) {
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
