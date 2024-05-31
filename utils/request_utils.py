# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/6/16
from urllib.parse import *

class Request(object):
    def __init__(self, raw:bytes):
        self.raw = raw
        self.method,self.path,self.headers,self.content,self.form = self._parse(raw)

    def _parse(self, raw:bytes):
        header,content = raw.split(b"\r\n\r\n",1)
        _, header = header.split(b"\r\n", 1)
        method,path = _.split()[:2]
        headers_dict = dict([[j.decode('utf-8') for j in i.split(b": ",1)] for i in  header.split(b"\r\n")])
        method = method.decode("utf-8")
        path = path.decode("utf-8")
        #print(method, path, headers_dict, content)
        if method == 'POST':
            form = {i.decode('utf-8'):j.decode("utf-8") for i,j in parse_qsl(content)}
        else:
            form = {}
        return method, path, headers_dict, content, form


if __name__ == '__main__':
    a = Request( b'POST /api/invite_camera HTTP/1.1\r\nHost: 11.4.14.15:5067\r\nUser-Agent: python-requests/2.27.1\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nConnection: keep-alive\r\nContent-Length: 101\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\ncam_url=gb28181%3A%2F%2F41100000002000009999%2F41017202001310602819&play_ip=127.0.0.1&play_port=27240')
    print(a.form)