#coding:utf-8
import socket
import thread
import urlparse
import select

BUFLEN = 8192



class Proxy(object):
    def __init__(self, conn, addr):
        self.source = conn
        self.request = ""
        self.headers = {}
        self.destnation = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.run()

#用来构造header
    def get_headers(self):
        header = ''
        while True:
            header += self.source.recv(BUFLEN)
            index = header.find('\n')
            if index > 0:
                break
        # firstLine,self.request=header.split('\r\n',1)
        firstLine = header[:index]
        self.request = header[index + 1:]
        self.headers['method'], self.headers['path'], self.headers['protocol'] = firstLine.split()

#用来发送请求
    def conn_destnation(self):
        url = urlparse.urlparse(self.headers['path'])
        hostname = url[1]
        port = "80"
        if hostname.find(':') > 0:
            addr, port = hostname.split(':')
        else:
            addr = hostname
        port = int(port)
        ip = socket.gethostbyname(addr)
        print ip, port
        self.destnation.connect(('127.0.0.1', 8080))  #可以填burpsuite的代理
        data = "%s %s %s\r\n" % (self.headers['method'], self.headers['path'], self.headers['protocol'])
        self.destnation.send(data + self.request)   #发送请求
        print data + self.request

#发送响应的结果
    def renderto(self):
        readsocket = [self.destnation]
        while True:
            data = ''
            (rlist, wlist, elist) = select.select(readsocket, [], [], 3)
            if rlist:
                data = rlist[0].recv(BUFLEN)
                if len(data) > 0:
                    self.source.send(data)#发送响应的结果
                else:
                    break
        # readsocket[0].close();

    def run(self):
        self.get_headers()
        self.conn_destnation()
        self.renderto()


class Server(object):

    def __init__(self, host, port, handler=Proxy):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(5)
        self.handler = handler

    def start(self):
        while True:
            try:
                conn, addr = self.server.accept()
                thread.start_new_thread(self.handler, (conn, addr))
            except:
                pass


if __name__ == '__main__':
    s = Server('127.0.0.1', 6666)   #这里写本地ip，监听的端口。
    s.start()