# TCP server
# socket()-->bind()-->listen()--accept()-->send()
import socket
import thread
#import threading

HOST = "127.0.0.1"
PORT = 50007
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(5)

def handle_tcp(conn, addr):
    print "New connection from %s:%s" % addr
    conn.send(b'Welcome to TCP echo server!')
    while 1:
        data = conn.recv(1024)
        if not data:
            break
        conn.send(b"Message from server: %s" %data)
    conn.close()

while 1:
    conn, addr = s.accept()
    thread.start_new_thread(handle_tcp, (conn, addr))
    #t = threading.Thread(target=handle_tcp, args=(conn,addr))
    #t.start()
