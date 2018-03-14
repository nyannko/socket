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
    remaining_header = struct.pack('!BBHHHH', 1, 0, 1, 0, 0, 0)
    qname = build_qname(domain_name)
    qtype_qclass = struct.pack('!HH', qtype, QCLASS_IN)
    return id + remaining_header + qname + qtype_qclass


def parse_name(data, offset):
    p = offset
    labels = []
    # \x03 length of label
    l = data[p]
    while l > 0:
        # \xc0\x0c pointer
        if (l & (128 + 64)) == (128 + 64):
            pointer = struct.unpack('!H', data[p:p + 2])[0]
            # the first two bits of offset
            pointer &= 0x3FFF
            r = parse_name(data, pointer)
            labels.append(r[1])
            p += 2
            # pointer is the end
            return p - offset, b'.'.join(labels)
        else:
            labels.append(data[p + 1:p + 1 + l])
            p += 1 + l
        l = data[p]
    return p - offset + 1, b'.'.join(labels)


def parse_record(data, offset, question=False):
    nlen, name = parse_name(data, offset)
    if not question:
        record_type, record_class, record_ttl, record_rdlength = struct.unpack(
            '!HHiH', data[offset + nlen:offset + nlen + 10]
        )
        ip = parse_ip(record_type, data, record_rdlength, offset + nlen + 10)
        return nlen + 10 + record_rdlength, \
               (name, ip, record_type, record_class, record_ttl)
    else:
        record_type, record_class = struct.unpack(
            '!HH', data[offset + nlen:offset + nlen + 4]
        )
        return nlen + 4, (name, None, record_type, record_class, None, None)


def parse_ip(addrtype, data, length, offset):
    if addrtype == QTYPE_A:
        return socket.inet_ntop(socket.AF_INET, data[offset:offset + length])


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


def parse_response(data):
    try:
        if len(data) >= 12:
            header = parse_header(data)
            if not header:
                return None
            res_id, res_qr, res_tc, res_ra, res_rcode, res_qdcount, \
            res_ancount, res_nscount, res_arcount = header

            qds = []
            ans = []
            offset = 12
            for i in range(0, res_qdcount):
                l, r = parse_record(data, offset, True)
                offset += l
                if r:
                    qds.append(r)
            for i in range(0, res_ancount):
                l, r = parse_record(data, offset)
                offset += l
                if r:
                    ans.append(r)
            for i in range(0, res_nscount):
                l, r = parse_record(data, offset)
                offset += l
            for i in range(0, res_arcount):
                l, r = parse_record(data, offset)
                offset += l
            print(qds)
            print(ans)
    except Exception as e:
        return None


def resolve(host):
    if (host != bytes):
        host = host.encode('utf-8')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    query = build_query(host, QTYPE_A)
    # b'\x83\xca\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01'

    dns_servers = get_resolv()
    sock.sendto(query, ('8.8.8.8', 53))
    # sock.sendto(query, (dns_servers[0], 53))

    res, addr = sock.recvfrom(1024)
    print(res)

    parse_response(res)


resolve('www.google.com')
# Answer:
# b'\x8b\xc2\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x94\x00\x04\xd8:\xd4\x84'
# b'IY\x81\x80\x00\x01\x00\x01\x00\r\x00\r\x03www\x06google\x03com\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x19\x00\x04\xac\xd9\x10D\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x14\x01l\x0cgtld-servers\x03net\x00\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01f\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01i\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01h\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01c\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01j\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01b\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01d\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01e\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01m\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01a\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01g\xc0>\xc0\x17\x00\x02\x00\x01\x00\x02\x9f\x94\x00\x04\x01k\xc0>\xc0|\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc06p\x1e\xc0l\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0+\xac\x1e\xc0\xcc\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0\x0c^\x1e\xc0\x9c\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc00O\x1e\xc0<\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0)\xa2\x1e\xc0\xbc\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0\x1fP\x1e\xc0\xfc\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0*]\x1e\xc1\x0c\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc04\xb2\x1e\xc0\xdc\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc07S\x1e\xc0\x8c\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0\x1a\\\x1e\xc0\\\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0#3\x1e\xc0\xec\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0\x05\x06\x1e\xc0\xac\x00\x01\x00\x01\x00\x02\x9f\x94\x00\x04\xc0!\x0e\x1e'

