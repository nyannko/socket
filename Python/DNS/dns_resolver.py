import socket
import os
import struct

# DNS message: Header(12) + Question(name+4) + Answer + Authority + Additional
# Header:
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                      ID                       |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    QDCOUNT                    |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    ANCOUNT                    |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    NSCOUNT                    |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# |                    ARCOUNT                    |
# +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
# Question: qname + qtype + qclass

QCLASS_IN = 1
QTYPE_A = 1

def get_resolv():
    with open('/etc/resolv.conf') as f:
        f = f.readlines()
        dns_servers = []
        for line in f:
            if not line.startswith('nameserver'):
                continue
            line = line.split()[1]
            dns_servers.append(line)
        return dns_servers

def build_qname(address):
    address = address.strip(b'.')
    labels = address.split(b'.')
    results = []
    for label in labels:
        l = len(label)
        # length octet
        results.append(chr(l).encode('utf-8'))
        results.append(label)
    results.append(b'\0')
    # [b'\x03', b'www', b'\x06', b'google', b'\x03', b'com', b'\x00']
    return b''.join(results)

def build_query(domain_name, qtype):
    id = os.urandom(2)
    remaining_header = struct.pack('!BBHHHH', 1,0,1,0,0,0)
    qname = build_qname(domain_name)
    qtype_qclass = struct.pack('!HH', qtype, QCLASS_IN)
    return id + remaining_header + qname + qtype_qclass


def parse_record(res, offset):
    # record_type, record_class, record_ttl, record_rdlength = struct.unpack("!HHiH", res[])
    pass
def parse_header(res):
    header = struct.unpack("!HHBBHHH", res[:12])
    res_id = header[0]
    res_qr = header[1] & 128
    res_tc = header[1] & 2
    res_ra = header[2] & 128
    res_rcode = header[2] & 15
    res_qdcount = header[3]
    res_ancount = header[4]
    res_nscount = header[5]
    res_arcount = header[6]
    return (res_id, res_qr, res_tc, res_ra, res_rcode, res_qdcount, res_ancount, res_nscount, res_arcount)

def parse_response(res):
    if(len(res) >= 12):
        header = parse_header(res)
        res_id, res_qr, res_tc, res_ra, res_rcode, res_qdcount, res_ancount, res_nscount, res_arcount = header
    offset = 12
    print(header)
    
    #for i in range(0, res_qdcount):


def resolve(host):
    if(host != bytes):
        host = host.encode('utf-8')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    query = build_query(host, QTYPE_A)
    # b'\x83\xca\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01'

    dns_servers = get_resolv()
    sock.sendto(query, ('8.8.8.8', 53))
    #sock.sendto(query, (dns_servers[0], 53))

    res, addr = sock.recvfrom(1024)
    print(res)

    parse_response(res)

resolve('www.google.com')
# Answer:
# b'\x8b\xc2\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x94\x00\x04\xd8:\xd4\x84'
# b'IY\x81\x80\x00\x01\x00\x01\x00\r\x00\r\x03www\x06google\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x19\x00\x04\xac\xd9\x10D\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x14\x01l\x0cgtld-servers\x03net\x00\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01f\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01i\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01h\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01c\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01j\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01b\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01d\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01e\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01m\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01a\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01g\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01k\xc0>\xc0|\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc06p\x1e\xc0l\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0+\xac\x1e\xc0\xcc\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0\x0c^\x1e\xc0\x9c\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc00O\x1e\xc0<\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0)\xa2\x1e\xc0\xbc\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0\x1fP\x1e\xc0\xfc\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0*]\x1e\xc1\x0c\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc04\xb2\x1e\xc0\xdc\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc07S\x1e\xc0\x8c\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0\x1a\\\x1e\xc0\\\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0#3\x1e\xc0\xec\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0\x05\x06\x1e\xc0\xac\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0!\x0e\x1e'

