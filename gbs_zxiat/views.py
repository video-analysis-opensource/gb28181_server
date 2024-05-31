# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/4/13
from django.http import  HttpResponse, HttpResponseRedirect
from django.shortcuts import  render_to_response,render
from django.core.paginator import Paginator
from django.utils.log  import  mail
from django.template import  Context,RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.csrf import  csrf_exempt
import json
from django.forms import model_to_dict
import re, os
import base64
from .models import *
from django.db.models import Q
from django.conf import settings
from django.core.paginator import InvalidPage
import time,copy
from django.contrib.staticfiles.views import serve as static_serve


def json_response(data):
    return HttpResponse(json.dumps(data),
                        content_type="application/javascript")


@login_required
def index(request):
    # 首页 - (视频树形图 +  多屏播放)
    return render(request, "index.html", locals())


@csrf_exempt
def data_handle(request):
    # 数据处理，入库
    # 并发量较高
    result = {"status": True, "message": "success", "data": None}
    try:
        info = request.body
        info = json.loads(info)
        assert len(info) > 0
        _type = info['type']
        data = info['data']
        if "query" in _type:
            if _type == 'device_catalog_query':
                # 如果是catalog查询消息
                code = data["gb_code"]
                _time = data["time"]
                GatewayInfo.objects.filter(code=code).update(last_scan_catalog_time=int(_time))
        else:
            code = data["gb_code"]
            GatewayInfo.objects.filter(code=code).update(last_msg_time=int(time.time()))
            if _type == 'device_deviceinfo':
                # 网关信息
                code = data["code"]
                manufacturer = data['manufacturer']
                _model = data['model']
                # print_to_logger(code, manufacturer, _model)
                GatewayInfo.objects.filter(code=code).update(manufacture=manufacturer, model=_model)
            if _type == "device_keepalive":
                # 心跳信息
                code = data["gb_code"]
                _time = data['time']
                _ = GatewayInfo.objects.get(code=code)
                _.heartbeat_time = int(_time)
                if not _.reg_time:
                    _.reg_time = int(_time)
                _.save()
            if _type == "device_catalog_dev":
                # catalog信息 - 设备
                code = data["code"]
                name = data["name"]
                manufacturer = data['manufacturer']
                ip = data['ip']
                port = data['port']
                lng = data['lng']
                lat = data["lat"]
                ptz_type = data['ptz_type'] or '3'
                is_online = 1 if data["is_online"] == True else 0
                raw_info = data["raw_info"]
                gb_code = data["gb_code"]
                _model = data["model"]
                parent_id = data['parent_id'] or ''
                if "/" in parent_id:
                    parent_id = parent_id.split("/")[-1]
                elif "\\" in parent_id:
                    parent_id = parent_id.split("\\")[-1]
                if parent_id == gb_code or parent_id == code:
                    parent_id = ''
                _time = data['time']
                _dev = GatewayInfo.objects.get(code=gb_code)
                try:
                    _node = DeviceNodeInfo.objects.get(code=code)
                except:
                    # 现在可以正常存入了。
                    _node = DeviceNodeInfo(code=code, gateway_code=gb_code,
                                                  is_dir=0, name=name,
                                                  manufacture=manufacturer,
                                                  model=_model, parent_node_id=parent_id,
                                                  ptz_type=ptz_type, lng=lng, lat=lat,
                                                  ip_address=ip, port=port, is_online=is_online,
                                                  addtime=int(_time),
                                                  update_time=int(_time),
                                                  raw_info=raw_info
                                                  )
                    _node.save()
                else:
                    _node.gateway_code = gb_code
                    _node.is_dir = 0
                    _node.name = name
                    _node.update_time = int(_time)
                    _node.manufacture = manufacturer
                    _node.model = _model
                    _node.parent_node_id = parent_id
                    _node.ptz_type = ptz_type
                    _node.lng = lng
                    _node.lat = lat
                    _node.ip_address = ip
                    _node.port = port
                    _node.is_online = is_online
                    _node.raw_info = raw_info
                    _node.save()

            if _type == 'device_catalog_dir':
                # catalog 信息 -目录
                code = data["code"]
                name = data["name"]
                raw_info = data["raw_info"]
                gb_code = data["gb_code"]
                parent_id = data['parent_id'] or ''
                business_id = data.get('business_groupid', '') or ''
                if "/" in parent_id:
                    parent_id = parent_id.split("/")[-1]
                elif "\\" in parent_id:
                    parent_id = parent_id.split("\\")[-1]
                if parent_id == gb_code or parent_id == code:
                    parent_id = ''
                if parent_id == business_id:
                    parent_id = ''
                _time = data['time']
                _dev = GatewayInfo.objects.get(code=gb_code)
                p = None
                try:
                    if parent_id:
                        if len(parent_id) < 20:
                            _c_ = [parent_id, parent_id[:-2], parent_id[:-4]]
                        else:
                            _c_ = [parent_id, code[:8], code[:6], code[:4]]
                        for _c in _c_:
                            try:
                                p = DeviceNodeInfo.objects.get(code=_c,
                                                                      gateway_code=gb_code,
                                                                      is_dir=1)
                                parent_id = _c
                                break
                            except:
                                pass
                    _node = DeviceNodeInfo.objects.get(code=code)
                except:
                    _node = DeviceNodeInfo(code=code, gateway_code=gb_code,
                                                  is_dir=1, name=name,
                                                  manufacture='',
                                                  model='', parent_node_id=parent_id,
                                                  addtime=int(_time),
                                                  update_time=int(_time),
                                                  raw_info=raw_info)
                    _node.save()
                else:
                    _node.gateway_code = gb_code
                    _node.is_dir = 1
                    _node.name = name
                    _node.update_time = int(_time)
                    _node.parent_node_id = parent_id
                    _node.raw_info = raw_info
                    _node.save()
    except Exception as e:
        result['status'] = False
        result['message'] = str(e)
    return HttpResponse(json.dumps(result), status=200,
                        content_type="application/json")


@csrf_exempt
def gb_gateway_devs(request):
    _db_gateway_info = {}
    _info = GatewayInfo.objects.all()
    for _ in _info:
        _db_gateway_info[_.code] = model_to_dict(_)
        _db_gateway_info[_.code]['mode'] = _.mode
    # 赋值
    gb_gateways = copy.deepcopy(_db_gateway_info)
    _gb_devs = {}
    _info = DeviceNodeInfo.objects.all().values("code", "gateway_code")
    for _ in _info:
        if _["gateway_code"] in gb_gateways:
            _gb_devs[_["code"]] = gb_gateways[_["gateway_code"]]
    return HttpResponse(json.dumps([gb_gateways,_gb_devs]),
                        content_type="application/json",
                        status=200)


def front_view(request, path):
    if not path:
        path = "/"
    if path[0] != "/":
        path = "/" + path
    if path.endswith("/"):
        return HttpResponseRedirect(path+"index.html")
    else:
        real_file_path = os.path.join("/front", "." + path)
        real_file_path = os.path.abspath(real_file_path)
        print(real_file_path)
        try:
            return static_serve(request, real_file_path)
        except:
            if path.startswith("/static/"):
                try:
                    static_serve(request, path.replace("/static/",''))
                except:
                    return HttpResponse("404!%s" % real_file_path, status=404)
            else:
                return HttpResponse("404!%s" % real_file_path, status=404)