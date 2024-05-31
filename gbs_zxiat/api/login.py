# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/4/24
# 登录/退出
from ..models import *
from ..decorators import *
from django.contrib.auth.models import *


@restful_api_deco()
def login(request):
    '''
    登录
    传参形式:POST
    参数说明：
    username  账号
    password  密码
    返回数据：
    返回核心数据中为True 代表登录成功  为False代表登录失败(登录失败会返回失败原因)
    '''
    post_info = request.POST
    username = post_info.get('username', '').strip()
    password = post_info.get('password', '').strip()
    assert username, FieldError('username','用户名不能为空')
    try:
        user = User.objects.get(username=username)
    except:
        raise FieldError('username', '用户%s不存在' % username)
    if not user.is_active:
        raise FieldError('username', '用户%s不允许登录系统' % username)
    if not password:
        raise FieldError('password','密码不能为空')
    if user.check_password(password):
        request.api_session['user_id'] = user.id
        print(request.api_session.items())
    else:
        raise FieldError('password', '密码不正确')
    # request.session['user_id'] =
    request.set_session_info = True
    return request.session_info


@restful_api_deco()
def is_login(request):
    # 当前是否是登录状态
    '''
    当前是否是登录状态
    传参形式:POST/GET
    参数: 无
    返回数据：
    返回核心数据中为True 代表当前已登录  为False代表未登录
    '''
    print(request.api_session,request.api_session.items(),
          request.api_session.sk)
    request.api_session['test'] = request.api_session.get('test',1) +1
    if request.user:
        return True
    else:
        return False


@restful_api_deco(login_required=True)
def my_info(request):
    '''
    获取当前登录用户的个人信息
    传参形式:POST/GET
    参数: 无
    返回数据：
    {'username':"admin","id":1}
    '''
    print(request.api_session,request.api_session.items(),
          request.api_session.sk)
    request.api_session['test'] = request.api_session.get('test',1) +1
    return {"username":  request.myuser.username, "id": request.myuser.id}



@restful_api_deco()
def logout(request):
    '''
    退出
    传参形式:POST/GET
    参数: 无
    '''
    if request.api_session.has_key('user_id'):
        request.api_session.pop('user_id')
    return True
