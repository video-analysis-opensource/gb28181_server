# coding:utf-8
__author__ = "zhou"
# create by zhou on 2021/5/24
# 装饰器相关
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import time
import traceback
from .utils.db_session import  ApiSessionStore
import hashlib
from django.contrib.auth.models import User
import random


class FieldError(Exception):
    '字段错误提示类，'
    def __init__(self, field_name, message):
        Exception.__init__(self)
        self.message = message
        self.field_name = field_name

    def __str__(self):
        return str("$fielderror" + json.dumps({"field_name": self.field_name,
                                               "message": self.message}))


API_SESSION = True


def restful_api_deco(jsonp:bool=True, cros:bool=True, login_required=False, regex_rule=None):
    "restful api专用装饰器"
    def real_deco(fun):
        fun.regex_rule = regex_rule
        @csrf_exempt
        def view(request):
            content_type = request.META.get('CONTENT_TYPE', '')
            if 'application/json' in content_type:
                try:
                    request.POST = json.loads(request.body.decode('utf-8'))
                    request.POST = {str(i): str(j) for i, j in request.POST.items()}
                except Exception as e:
                    print(str(e))
                    pass
            request.set_session_info = False
            if API_SESSION:
                session_info = request.META.get("HTTP_SESSION", "") or request.GET.get("session", "") or \
                               request.GET.get("Session", "") or request.GET.get("SESSION", "") or \
                               request.META.get('HTTP_SESSION_KEY', '')
                #request.session = session_info

                if not session_info:
                    session_info = hashlib.md5((str(time.time()) +
                                                        str(random.random())).encode('utf-8')).hexdigest()
                request.session_info = session_info
                    #set_session_info = True
                    #request.session =
                #else:
                request.api_session = ApiSessionStore(session_key=hashlib.md5(
                    session_info.encode('utf-8')).hexdigest())
                    #print(request.session.items())]
                #request.session = request.api_session
            else:
                pass
            if request.method == "OPTIONS" :
                data = {}
            else:
                data = {"status": True, 'message': 'success', 'data': None, 'errorCode': None}
                try:
                    if API_SESSION:
                        value = request.api_session.get("user_id")
                    else:
                        value = request.api_session.get('user_id')
                    uid = int(value)
                    user = User.objects.get(id=uid, is_active=True)
                    request.myuser = user
                    request.user = user
                except:
                    request.myuser = None
                    request.user = None
                if request.method == "OPTIONS":
                    _result = {}
                else:
                    if login_required and not request.myuser:
                        data = {"status": False, 'message': '当前未登陆，不允许的操作',
                                'data': None, 'errorCode': 403 }
                    else:
                        try:
                            result = fun(request)
                            json.dumps(result)
                        except FieldError as _e:
                            data['status'] = False
                            data['message'] = str(_e.message)
                            data['formError'] = {"name": _e.field_name, "message": _e.message}
                            data['errorCode'] = 500
                        except Exception as e:
                            if type(e) == AssertionError and  str(e).startswith("$fielderror"):
                                _re_info = str(e).strip("$fielderror")
                                _re_info = json.loads(_re_info)
                                data['status'] = False
                                data['message'] = _re_info["message"]
                                data['formError'] = {"name": _re_info["field_name"], "message": _re_info["message"]}
                                data['errorCode'] = 500
                            else:
                                data["status"] = False
                                data["message"] = str(e)
                                data["traceback"] = traceback.format_exc()
                                data['errorCode'] = 500
                        else:
                            data['data'] = result
                data = json.dumps(data)
                # jsonp 相关逻辑
                if request.method == 'GET' and  'callback' in request.GET and jsonp:
                    data = "%s(%s)" % (request.GET["callback"], data)

            rsp = HttpResponse(data, content_type="application/json")
            # 允许跨域相关逻辑
            if cros and request.method in ('POST', 'OPTIONS', 'GET') and "HTTP_ORIGIN" in request.META:
                rsp["Access-Control-Allow-Origin"] = request.META.get("HTTP_ORIGIN")
                rsp["Access-Control-Allow-Methods"] = "OPTIONS, GET, POST"
                rsp["X-Requested-With"] = "XMLHttpRequest"
                rsp["Access-Control-Allow-Headers"] = "x-requested-with,session,Session,Content-Type," \
                                                      "Accept,Origin,X-Cookie,Session-Key"
                rsp["Access-Control-Max-Age"] = "86400"
                rsp["Access-Control-Allow-Credentials"] = 'true'
                rsp["Content-Type"] = "application/json; charset=utf-8"
            if request.set_session_info:
                request.api_session.save()
            rsp['Set-Session-Key'] = request.session_info
            return rsp
        view.fun = fun
        view.regex_rule = regex_rule
        view.__doc__ = fun.__doc__
        view.login_required = login_required
        return view
    return real_deco

