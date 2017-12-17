#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <sys/epoll.h>
#include <errno.h>
#include <ctype.h>

//#include<sys/types.h>
//#include<sys/socket.h>
//#include<netinet/in.h>
#include <arpa/inet.h>

#define SERV_PORT 3400
#define OPEN_MAX 65525
#define MAXLINE 80

int main(void) {

	int i, j, listenfd, connfd, sockfd;
	int n;
	ssize_t nready, efd, res;
	char buf[MAXLINE], str[INET_ADDRSTRLEN];
	socklen_t clilen;
	int client[OPEN_MAX];
	struct sockaddr_in servaddr, cliaddr;
	struct epoll_event tep, ep[OPEN_MAX];

	//Create socket
	listenfd = socket(AF_INET, SOCK_STREAM, 0);

	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servaddr.sin_port = htons(SERV_PORT);

	//Bind socket
	bind(listenfd,(struct sockaddr*)&servaddr, sizeof(servaddr));

	//Listen
	listen(listenfd, 10);
	printf("Server start listening on prot 3400\n");

	//Create epoll, efd is the root node of the red blacktree
	efd = epoll_create(OPEN_MAX);
	if(efd == -1) {
		perror("epoll_create error");
		exit(1);
	}

	//Add lfd to tree
	tep.events = EPOLLIN;
	tep.data.fd = listenfd;
	res = epoll_ctl(efd, EPOLL_CTL_ADD, listenfd, &tep);
	if(res == -1) {
		perror("epoll_ctl error");
		exit(1);
	}

	while(1) {
		nready = epoll_wait(efd, ep, OPEN_MAX, -1);
		if(nready == -1) {
			perror("epoll_wait error");
			exit(1);
		}
		for(i =0; i < nready; i++) {
			if(ep[i].data.fd == listenfd) {
				clilen = sizeof(cliaddr);
				connfd = accept(listenfd, (struct sockaddr *)&cliaddr, &clilen);
				printf("Connection from %s, port %d\n",inet_ntop(AF_INET, &cliaddr.sin_addr, str, sizeof(str)), ntohs(cliaddr.sin_port));

				tep.events = EPOLLIN;
				tep.data.fd = connfd;
				res = epoll_ctl(efd, EPOLL_CTL_ADD, connfd, &tep);
			} else {
				sockfd = ep[i].data.fd;
				n = read(sockfd, buf, MAXLINE);
				write(STDOUT_FILENO, buf, n); 
				//printf("Message from client: %s", buf); //????
				//n = recv(sockfd, &buf, sizeof(buf), 0);
				//Delete client from tree
				if(n == 0) {
					res = epoll_ctl(efd, EPOLL_CTL_DEL, sockfd, NULL);
					close(sockfd);
					printf("client[%d] closed connection\n",j);
				}else if(n < 0) {
					perror("receive < 0 error:");
					res = epoll_ctl(efd, EPOLL_CTL_DEL, sockfd, NULL);
					close(sockfd);
				} else {
					for(j = 0; j < n; j++) {
						buf[j] = toupper(buf[j]);
					}
						write(sockfd, buf, n);
						//send(sockfd, buf, sizeof(buf),0);
				}
			}
		}
	}
}
