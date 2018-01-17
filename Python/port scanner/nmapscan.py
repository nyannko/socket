# Nmap scanner
import json
import threading
from nmap import PortScanner

Host = "nyannko.tk"
Port = [21,22,23,25,58,80,443,2000]

def nmapScan(Host, Port):
    scanner = PortScanner()
    result = scanner.scan(Host, Port)
    print json.dumps(result, indent = 4)
    #print result["scan"]["106.39.41.16"]["tcp"]

def main():
    for port in Port:
        t = threading.Thread(target=nmapScan,args=(Host,str(port)))
        t.start()

if __name__ == '__main__':
    main()
