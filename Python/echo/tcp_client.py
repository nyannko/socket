# TCP client
# socket()-->connect()-->recv()
import socket

# server address
HOST = "127.0.0.1"
PORT = 50007

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

welcome = s.recv(1024)
print welcome 

while 1:
    data = raw_input("Send a message to server: ")
    s.send(data)
    print s.recv(1024)

s.close()
