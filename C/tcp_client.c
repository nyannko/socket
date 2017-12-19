#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <errno.h>
#include <ctype.h>

int main(int argc, char* argv[]) {
        //Create a socket
        int network_socket = socket(AF_INET, SOCK_STREAM, 0);

        struct sockaddr_in server_address;
        server_address.sin_family = AF_INET;
        server_address.sin_port = htons(atoi(argv[1]));
        //server_address.sin_addr.s_addr = INADDR_ANY;
        server_address.sin_addr.s_addr = inet_addr(argv[2]);

        //Check connection status
        int connect_status = connect(network_socket, (struct sockaddr *) &server_address, sizeof(server_address));
        if(connect_status == -1) {
                printf("error");
        }

        while(1) {
                //Send messages to server
                char messages[256];
                fgets(messages, 256, stdin);
                //send(network_socket, messages, sizeof(messages),0);
		int n = write(network_socket, messages, strlen(messages)); //send the length of the messages to server
		if(n < 0) {
		 	perror("Error writing to socket");
		}

                //Receive data from server
                char server_response[256];
		//recv(network_socket, &server_response, sizeof(server_response), 0);
		n = read(network_socket, server_response, sizeof(server_response)); //get response from socket in the char array
		if(n < 0) {
			perror("Error reding from socket");
		}

                //Print out the result returned from server
		//printf("Message from server: %s", server_response); will print random characters
		write(STDOUT_FILENO, server_response, n);
        }

        //Close socket
        close(network_socket);

        return 0;
}
