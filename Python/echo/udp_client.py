# UDP client
import socket

HOST = "127.0.0.1"
PORT = 50008

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while 1:
    data = raw_input("Send a message to server: ")
    s.sendto(data, (HOST, PORT))
    print(s.recv(1024))

s.close()
