from socket import *
from multiprocessing import Process, Manager
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import select
import os

TCP_IP = '127.0.0.1'
TCP_PORT = 8080
BUFFER_SIZE = 4096

RecvChange = {}
RecvChange['test.gilgil.net'] = ('hacking', 'ABCDEFG')
RecvChange['search.daum.net'] = ('Michael', 'GILBERT')

SendChange = {}
SendChange['search.daum.net'] = ('Accept-Encoding: gzip', 'Accept-Encoding:     ')

cacheFilter = set(['png', 'jpg', 'swf', 'jpeg'])
cacheData = {}

class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

def proc(from_client, from_server):
    
    tmp = ''
    from_server.val = ''
    request_from_client = HTTPRequest(from_client)
    host = request_from_client.headers['host']

    if(host.find(':')==-1): # default port : 80
        url = host
        port = 80
    else:
        url = host[:host.find(':')]
        port = int(host[host.find(':')+1:])

    effectiveURL = url
    if(effectiveURL.find('?')!=-1):
        effectiveURL = effectiveURL[:effectiveURL.find('?')]

    #B - send data change
    if effectiveURL in SendChange.keys():
        from_server.val = from_server.val.replace(SendChange[url][0], SendChange[url][1])

    # A - proxy(forward)
    a = socket(AF_INET, SOCK_STREAM)
    a.connect((url, port))
    a.send(from_client) # send to server
    
    while True:
        r, _, _ = select.select([a],[],[],1)
        if r:
            tmp = a.recv(BUFFER_SIZE) # recv from server
        else:
            break
        if not tmp:
            break
        from_server.val += tmp

    # B - recv data change
    if effectiveURL in RecvChange.keys():
        from_server.val = from_server.val.replace(RecvChange[url][0], RecvChange[url][1])

    #
    a.close()

if __name__ == '__main__':
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    #s.setblocking(0)
    manager = Manager()
    s.bind((TCP_IP, TCP_PORT))
    s.listen(200) # 200 queues
    p = '' #for process
    from_server = manager.Namespace()
    from_server.val = ''
    while True:
        conn, addr = s.accept()
        tmp = ''
        from_client = ''
        print '[+] Connection address:', addr
        print '[+] Receiving from client'
        while True:
            r, _, _ = select.select([conn],[],[],1)
            if(r):
                print '[+] Have some data'
                tmp = conn.recv(BUFFER_SIZE) # recv from client
            else:
                print '[+] No data to receive'
                break
            if not tmp:
                break
            print "received data:", tmp
            from_client += tmp
        print '[+] Receive Done'
        print '[+] From Client '
        print from_client
        print '[+] Fork process start'
        p = Process(target=proc, args=(from_client, from_server))
        p.start()
        p.join()
        print '[+] Fork process finish'
        print '[+] response from server'
        print from_server.val
        conn.send(from_server.val)  # send to client
        conn.close()

