# SOCKS5 server
import logging
import socket
import struct
import select
import threading

HOST = "127.0.0.1"
PORT = 50000

def send_data(sock, data):
#    print(data)
    bytes_sent = 0
    while True:
        r = sock.send(data[bytes_sent:])
        if r < 0:
            return r
        bytes_sent += r
        if bytes_sent == len(data):
            return bytes_sent


def handle_tcp(sock, remote):
    try:
        fdset = [sock, remote]
        while True:
            r, w, e = select.select(fdset, [], [])
            if sock in r:
                data = sock.recv(4096)
                if len(data) <= 0:
                    break
                result = send_data(remote, data)
                if result < len(data):
                    raise Exception('failed to send all data')

            if remote in r:
                data = remote.recv(4096)
                if len(data) <= 0:
                    break
                result = send_data(sock, data)
                if result < len(data):
                    raise Exception('failed to send all data')
    except Exception as e:
        raise(e)
    finally:
        sock.close()
        remote.close()


def handle_con(sock, addr):

    sock.recv(256)
    # send success to client
    sock.send(b"\x05\x00")
    data = sock.recv(4)
    
    # check CMD mode
    mode = ord(data[1])
    if mode != 1:
        print "Not a TCP connection."
        return 

    # handle address type
    addr_type = ord(data[3])

    # IPv4
    if addr_type == 1:
        addr_ip = sock.recv(4)
        remote_addr = socket.inet_ntoa(addr_ip)

    # domain name
    elif addr_type == 3:
        addr_len =  ord(sock.recv(1))
        remote_addr = sock.recv(addr_len)

    # IPv6
    elif addr_type == 4:
        addr_ip = sock.recv(16)
        remote_addr = socket.inet_ntop(socket.AF_INET6, addr_ip)
    else:
        return

    # DST.PORT
    remote_addr_port = struct.unpack('>H', sock.recv(2))

    reply = b"\x05\x00\x00\x01"
    reply += socket.inet_aton('0.0.0.0') + struct.pack(">H", PORT)
    sock.send(reply)

    try:
        remote = socket.create_connection((remote_addr, remote_addr_port[0]))
        logging.info('connecting %s:%d' % (remote_addr, remote_addr_port[0]))
    except socket.error as e:
        logging.error(e)
        return

    handle_tcp(sock, remote)


def main():
    socketServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    socketServer.bind((HOST, PORT))
    socketServer.listen(5)

    try:
        while True:
            sock, addr = socketServer.accept()
            print "Connection from %s:%s" % addr
            t = threading.Thread(target=handle_con, args=(sock, addr))
            t.start()
    except socket.error as e:
        logging.error(e)
    except KeyboardInterrupt:
        socketServer.close()


if __name__ == '__main__':
    main()
