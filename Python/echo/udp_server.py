# UDP server
import socket

HOST = "127.0.0.1"
PORT = 50008

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((HOST, PORT))

while 1:
    data, addr = s.recvfrom(1024)
    print("Connection from %s:%s" % addr)
    s.sendto(b"Message from server: %s" % data, addr)

s.close()
