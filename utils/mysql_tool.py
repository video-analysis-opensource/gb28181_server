# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/4/24
# mysql 操作工具
import gevent
from gevent.monkey import patch_all;patch_all()
import socket
print(socket.socket)