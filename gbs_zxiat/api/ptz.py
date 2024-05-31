# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/6/2
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
def ptz_control(request):
    '''云台控制接口
    调用形式：POST
    参数说明：
    id    摄像头id
    action     操作 ，可选值 ("left", "right", 'up', 'down',    # 上下左右 
                      'leftup', 'leftdown', "rightup", "rightdown",  # 左上  左下  右上  右下
                      'big', 'small',   # 变焦-拉近   变焦-变远
                      'stop')  # 停止转动
    speed      速度  10 -100 . 默认值36
    zoom_speed  变焦速度   1 -100   默认值3
    ''' # todo
    post_info = request.POST
    cam_url = post_info.get("cam_url", '')
    id = post_info.get("id", '')
    action = post_info.get("action", '')
    assert action in ("left", "right", 'up', 'down',
                      'leftup', 'leftdown', "rightup", "rightdown",
                      'big', 'small',
                      'stop')
    speed = post_info.get("speed", '') or '30'
    zoom_speed = post_info.get('zoom_speed', '') or '3'
    speed = int(speed)
    zoom_speed = int(zoom_speed)
    assert cam_url  or id
    if id:
        cam_url = "gb28181://{}/{}".format(*id.split("_"))
    api_url = "http://{}:{}/api/ptz_control".format(config.SIP_SERVER_IP, config.SIP_SERVER_API_PORT)
    requests.post(api_url, data={'cam_url': cam_url,
                                 'speed': speed,
                                 'zoom_speed': zoom_speed,
                                 'action': action},  timeout=2)
    return True
