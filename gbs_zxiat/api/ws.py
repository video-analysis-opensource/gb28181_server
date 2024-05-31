# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/6/10
from ..decorators import restful_api_deco,FieldError
from ..models import *
import copy
from django.forms.models import model_to_dict
from django.db.models import Q
import time,datetime
import re
from django.conf import settings
from gbs_zxiat.settings import config
from urllib import parse
import requests


@restful_api_deco(login_required=False)
def get_websocket_info(request):
    '''
    获取websocket配置信息。
    返回
    {"status": true, "message": "success", "data":
    {"port": 8005, "url": "ws://127.0.0.1:8005/ws/", "path": "/ws/"},
    "errorCode": null}
    '''
    ip = request.get_host().split(":")[0]
    ws_port = config.HTTP_WEBSOCKET_PORT
    # print(a)
    return {"port": ws_port,
            "url": f"ws://{ip}:{ws_port}/ws/",
            'path': "/ws/"}
