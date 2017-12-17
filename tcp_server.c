#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <errno.h>
#include <ctype.h>

int main(int argc, char *argv[]) {

	//Create server messages
	char server_messages[256]; 

	//Create server socket    
	int server_socket = socket(AF_INET, SOCK_STREAM, 0);

	struct sockaddr_in server_address, client_address;
	server_address.sin_family = AF_INET;
	server_address.sin_port = htons(3400);
	server_address.sin_addr.s_addr = INADDR_ANY;

	//Bind socket to specified IP and PORT
	bind(server_socket, (struct sockaddr*) &server_address, sizeof(server_address));

	listen(server_socket, 5);

	int client_socket;
	socklen_t client_length;
	client_length = sizeof(client_address);
	client_socket = accept(server_socket, (struct sockaddr*) &client_address, &client_length);
	while(1){
		if(client_socket < 0) error("error on accept");
		//Read messages from client
		//recv(client_socket, &server_messages, sizeof(server_messages), 0);
		int n = read(client_socket, server_messages, sizeof(server_messages));
		if(n == -1) {
			perror("read failed");
		}

		printf("Message from client: %s",server_messages);
		n = write(client_socket, server_messages, strlen(server_messages));
		printf("Sent %d bytes to client : %s\n", n, inet_ntoa(client_address.sin_addr));
		if(n == -1) {
			perror("write failed");
		}
		//send(client_socket, server_messages, sizeof(server_messages), 0);
	}
	return 0;
}
