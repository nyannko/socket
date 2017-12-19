# SOCKS5 client
import socks
s = socks.socksocket() 
s.set_proxy(socks.SOCKS5, "localhost", 50000)

# s.connect(("180.149.134.141",80))
# s.connect(("172.217.17.78",443))
s.connect(("nyannko.tk", 443))
s.sendall("GET / HTTP/1.1 /r/n/r/n")
print s.recv(4096)
