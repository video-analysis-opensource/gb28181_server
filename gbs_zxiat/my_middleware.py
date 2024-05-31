# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/6/10
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import sys

class MyMiddleware(MiddlewareMixin):
    def __init__(self, *args, **kwargs):
        MiddlewareMixin.__init__(self, *args, **kwargs)


    def process_request(self, request):
        sys.django_host = request.get_host()
