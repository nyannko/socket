# Simple port scanner
import socket
import threading

HOST = 'nyannko.tk'    
PORTS = [21, 22, 23, 25, 53, 58, 80, 443, 2000] 

screenLock = threading.Semaphore(value=1)
def portScan(HOST, PORT):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.send('hello, are you open?')
        # the length of received data
        data = s.recv(100)
        screenLock.acquire()
        print PORT,'port opened'
    except:
        screenLock.acquire()
        print PORT,'port closed'
    finally:
        screenLock.release()
        s.close()

def main():
    for PORT in PORTS:
        t = threading.Thread(target=portScan,args=(HOST, PORT))
        t.start()

if __name__=='__main__':
    main()
