# HTTP proxy
from http.server import BaseHTTPRequestHandler, HTTPServer
from urlpath import URL
import socket
import urllib

HOST = "127.0.0.1"
PORT = 8000

# Run `curl -x http://127.0.0.1:8000 http://www.moe.edu.cn' to test proxy

class ProxyHandler(BaseHTTPRequestHandler):

    # GET method
    def do_GET(self):
        # todo add try catch here
        url = URL(self.path)
        ip = socket.gethostbyname(url.netloc)
        port = url.port
        if port is None:
            port = 80
        path = url.path
        print("Connected to {} {} {}".format(url ,ip ,port))

        # close connection
        del self.headers["Proxy-Connection"]
        self.headers["Connection"] = "close"

        # reconstruct headers
        send_data = "GET " + path + " " + self.protocol_version + "\r\n"

        header = ""
        for k, v in self.headers.items():
            header += "{}: {}\r\n".format(k, v)
        send_data += header + "\r\n"

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        s.connect((ip, port))
        s.sendall(send_data.encode())

        # receive data from remote
        received_data = b""
        while 1:
            data = s.recv(4096)
            if not data:
                break
            received_data += data

        s.close()

        # send data to client
        self.wfile.write(received_data)

def main():
    try:
        server = HTTPServer((HOST, PORT), ProxyHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == "__main__":
    main()
