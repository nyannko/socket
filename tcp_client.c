#include<stdio.h>
#include<stdlib.h>

#include<sys/types.h>
#include<sys/socket.h>

//Struct for handling internet addresses
#include<netinet/in.h>

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
		send(network_socket, messages, sizeof(messages),0);

		//Receive data from server
		char server_response[256];
		recv(network_socket, &server_response, sizeof(server_response), 0);

		//Print out the result returned from server
		printf("Message from server: %s", server_response);
	}

	//Close socket
	close(network_socket);

	return 0;
}
