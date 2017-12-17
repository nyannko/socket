all:
	gcc tcp_server.c -o tcp_server
	gcc tcp_client.c -o tcp_client
	gcc tcp_epollserver.c -o tcp_epollserver
