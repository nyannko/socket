# HTTPS proxy
from http.server import BaseHTTPRequestHandler, HTTPServer
import select
import socket

HOST = "127.0.0.1"
PORT = 8888
server_class = HTTPServer

# Run `curl -x http://127.0.0.1:8888 https://www.google.com` to test proxy

# Inherit from BaseHTTPRequestHandler
class ProxyHandler(BaseHTTPRequestHandler):

    # returns the length of data
    def send_data(self, sock, data):
        length = sock.send(data)
        return length

    def handle_tcp(self, sock, remote):
        try:
            fdset = [sock, remote]
            while 1:
                r, w, e = select.select(fdset, [], [])
                if sock in r:
                    data = sock.recv(4096)
                    if len(data) <= 0:
                        break
                    result = self.send_data(remote, data)
                    if result < len(data):
                        raise Exception('failed to send all data')

                if remote in r:
                    data = remote.recv(4096)
                    if len(data) <= 0:
                        break
                    result = self.send_data(sock, data)
                    if result < len(data):
                        raise Exception('failed to send all data')
        except Exception as e:
            raise(e)
        finally:
            sock.close()
            remote.close()

    def do_CONNECT(self):
        # Get request ip and port from client 
        url = self.path.split(":")[0]
        port = self.path.split(":")[1]
        ip = socket.gethostbyname(url)
        port = int(port)

        print(url, ip, port)
        remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        remote.connect((ip, port))

        self.wfile.write("{protocol_version} 200 Connection Established\r\n\r\n".format(protocol_version=self.protocol_version).encode())
        self.handle_tcp(self.connection, remote)


def main():
    httpd = server_class((HOST,PORT), ProxyHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
