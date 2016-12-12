from socket import *
from multiprocessing import Process, Manager
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
import select
import os

TCP_IP = '127.0.0.1'
TCP_PORT = 8080
BUFFER_SIZE = 1024

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
    #todo

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
    while 1:
        conn, addr = s.accept()
        tmp = ''
        from_client = ''
        print '[+] Connection address:', addr
        print '[+] Receiving from client'
        while 1:
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

