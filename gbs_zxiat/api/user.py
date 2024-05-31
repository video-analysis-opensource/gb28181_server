# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/6/2
from ..decorators import restful_api_deco,FieldError
from ..models import *



@restful_api_deco(login_required=True)
def change_passwd(request):
    '''
    重置密码
    传参形式:POST
    参数:
    passwd      密码
    re_passwd   再次输入密码
    返回数据：
    返回核心数据中为True 代表密码重置成功  。如果失败 返回结果会有失败原因

    '''
    post_info = request.POST
    passwd = post_info.get("passwd", "")
    re_passwd = post_info.get("re_passwd", "")
    assert len(passwd) >=6, FieldError('passwd', "密码长度必须不少于6位")
    assert passwd == re_passwd, FieldError('re_passwd', '两次输入的密码不一致')
    request.user.set_password(passwd)
    return True
