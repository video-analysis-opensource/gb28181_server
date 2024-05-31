# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/5/23
from ..decorators import restful_api_deco,FieldError
from ..models import *
import copy
from django.forms.models import model_to_dict
from django.db.models import Q
import time,datetime
import re

login_required = False

@restful_api_deco(login_required=login_required)
def sub_dir_info(request):
    '''
    获取子目录信息
    '''
    # 本域
    result = []
    # 把所有CustomSubDir信息写入到result中并排序
    infos = {i.dir_code_id:i for i in CustomSubDir.objects.all()}
    for a in infos.values():
        result.append({"id": a.dir_code_id,
                       "name":a.name,
                       "parent":a.parent_id or "00000000000000000000",
                       #'pId':a.parent_id or "00000000000000000000"
                       })
    result.sort(key=lambda x:x['parent'])
    # 真正的结果变量
    final_result = [{"id":"00000000000000000000" ,"name":"本域", "parent": None, "is_dir":True}]
    # 结果筛选， 并append到 final_result中
    #print(result)
    for index_,i in enumerate(copy.deepcopy(result)):
        #print(i["parent"])
        if i["parent"] != '00000000000000000000' and i['parent'] not in infos:
            pass
        else:
            i["is_dir"] = True
            final_result.append(i)
    # 临时存所有的目录id。
    ids = [i["id"]  for i in final_result]
    gateway_info = GatewayInfo.objects.all()
    # 查出所有网关信息，并把其放入到final_result
    for i in gateway_info:
        if not i.dir_code_id.strip():
            final_result.append({"id": i.code, "name":i.name, "parent": '00000000000000000000', "is_dir":False})
        else:
            if i.dir_code_id  and i.dir_code_id in ids and i.code not in ids:
                final_result.append({"id": i.code, "name": i.name,
                               "parent": str(i.dir_code_id),"is_dir": False})
    return final_result


@restful_api_deco(login_required=login_required)
def add_dir(request):
    #增加目录
    post_info = request.POST
    parent = post_info.get("parent_id")
    code = post_info.get("code")
    name = post_info.get("name")
    assert name, FieldError("name","目录名不能为空！")
    assert CustomSubDir.objects.filter(name=name).count() == 0 and \
    GatewayInfo.objects.filter(name=name).count()==0, FieldError("name",'目录名不能和现有网关/目录重复。')
    try:
        assert len(code) <= 20
        int(code)
    except:
        raise FieldError("code", "国标编码必须是20位以内的数字")
    assert CustomSubDir.objects.filter(dir_code_id=code).count() == 0 and \
           GatewayInfo.objects.filter(code=code).count() == 0, FieldError("code", '国标编码不能和现有网关/目录重复。')
    assert parent == '0'*20 or CustomSubDir.objects.filter(dir_code_id=parent).count() == 1, FieldError("parent",
                                                                                                        "父目录不存在！请重试！")
    _ = CustomSubDir(dir_code_id=code, parent_id=parent, name=name,addtime=int(time.time()))
    _.save()
    return True


@restful_api_deco(login_required=login_required)
def edit_dir(request):
    #  增加目录
    post_info = request.POST
    old_code = post_info.get("old_code")
    code = post_info.get("code")
    name = post_info.get("name")
    assert name, FieldError("name", "目录名不能为空！")
    assert CustomSubDir.objects.filter(dir_code_id=old_code).count() == 1,\
        FieldError("old_code","该目录已不存在，请刷新页面后重试")
    assert CustomSubDir.objects.filter(~Q(dir_code_id=old_code),name=name).count() == 0 and \
           GatewayInfo.objects.filter(name=name).count() == 0, FieldError("code", '目录名不能和现有网关/目录重复。')
    try:
        assert len(code) <= 20
        int(code)
    except:
        raise FieldError("code", "国标编码必须是20位以内的数字")
    if code != old_code:
        # raise FieldError("code","不允许修改国标编码！")
        assert CustomSubDir.objects.filter(dir_code_id=code).count() == 0 and \
               GatewayInfo.objects.filter(code=code).count() == 0, FieldError("code", '国标编码不能和现有网关/目录重复。')
        CustomSubDir.objects.filter(dir_code_id=old_code).update(dir_code_id = code)
        CustomSubDir.objects.filter(parent_id=old_code).update(parent_id=code)
        #_.dir_code_id = code
        #print("new code", old_code, code)
        #_.save()

    _ = CustomSubDir.objects.get(dir_code_id=code)
    _.name = name
    _.save()
    return True


@restful_api_deco(login_required=login_required)
def del_dir(request):
    #删除目录
    post_info = request.POST
    code = post_info.get("code")
    assert GatewayInfo.objects.filter(dir_code_id=code).count() == 0 ,FieldError("code","当前目录非空，不允许删除！")
    assert CustomSubDir.objects.filter(parent_id=code).count() == 0, FieldError("code", "当前目录非空，不允许删除！")
    CustomSubDir.objects.filter(dir_code_id=code).delete()
    return True


@restful_api_deco(login_required=login_required)
def all_gateway_info(request):
    '''
    所有的网关设备信息
    '''
    # 本域
    result = []
    # 把所有CustomSubDir信息写入到result中并排序
    infos = {i.dir_code_id: i for i in CustomSubDir.objects.all()}
    for a in infos.values():
        result.append({"id": a.dir_code_id,
                       "name": a.name,
                       "parent": a.parent_id or "00000000000000000000",
                       })
    result.sort(key=lambda x: x['parent'])
    # 真正的结果变量
    dir_result = [{"id": "00000000000000000000", "name": "本域", "parent": None,"is_dir":True}]
    # 结果筛选， 并append到 final_result中
    for index_, i in enumerate(copy.deepcopy(result)):
        if i["parent"] != '00000000000000000000' and i['parent'] not in infos:
            pass
        else:
            i["is_dir"] = True
            dir_result.append(i)
    # 临时存所有的目录id。
    ids = {i["id"]:i for i in dir_result}
    gateway_info = GatewayInfo.objects.all()
    gateway_result = []
    # 查出所有网关信息，并把其放入到final_result
    for i in gateway_info:
        _i = model_to_dict(i)
        _i["is_online"] = i.is_online
        if not i.dir_code_id.strip():
            _i["parent"] = {"id": "00000000000000000000", "name": "本域", "parent": None,"is_dir":True}
            gateway_result.append(_i)
        else:
            if i.dir_code_id and i.dir_code_id in ids and i.code not in ids:
                _i["parent"] = ids[i.dir_code_id]
                gateway_result.append(_i)
    return gateway_result



@restful_api_deco(login_required=login_required)
def query_gateway_info(request):
    '''
    根据parent_id 查询其下属的网关。
    传参形式： POST
    参数：
    parent_id      父ID
    :param request:
    :return:
    '''
    post_info = request.POST
    parent_id = post_info.get("parent_id", '') or '00000000000000000000'
    all_dir = CustomSubDir.objects.all()
    _ = [(i.dir_code_id, i.parent_id) for i in all_dir]
    parent_ids = [parent_id]
    for i in range(30):
        for j,k in _:
            if k in parent_ids:
                parent_ids.append(j)
    gateway_info = GatewayInfo.objects.all()
    gateway_result = []
    # 查出所有网关信息，并把其放入到final_result
    for i in gateway_info:
        _i = model_to_dict(i)
        _i["is_online"] = i.is_online
        if parent_id != '00000000000000000000':
            if i.dir_code_id in parent_ids or  i.code == parent_id:
                gateway_result.append(_i)
        else:
            gateway_result.append(_i)
        # else:
        #     if i.dir_code_id and i.dir_code_id in ids and i.code not in ids:
        #         _i["parent"] = ids[i.dir_code_id]
        #         gateway_result.append(_i)
    return gateway_result


@restful_api_deco(login_required=login_required)
def get_gateway_info(request):
    '''
    根据parent_id 获取网关信息
    传参形式： POST
    参数：
    code    国标编码
    :param request:
    :return:
    '''
    post_info = request.POST
    code = post_info.get("code", '')
    gateway_info = GatewayInfo.objects.get(code=code)
    # gateway_result = []
    _i = model_to_dict(gateway_info)
    _i["is_online"] = gateway_info.is_online
    return _i


@restful_api_deco(login_required=login_required)
def add_gateway(request):
    #增加下级设备
    post_info = request.POST
    name = post_info.get("name",'').strip()
    dir_code_id = post_info.get("dir_code_id", "").strip()
    code = post_info.get("code",'').strip()
    ip = post_info.get("ip",'').strip()
    port = post_info.get("port", "").strip()
    limit_ipport = post_info.get("limit_ipport", "0").strip()
    # is_wandev = post_info.get("is_wandev", "").strip()
    rtp_mode = post_info.get("rtp_mode", "").strip()
    assert name ,FieldError("name", "目录名不能为空")
    assert CustomSubDir.objects.filter(name=name).count() == 0 and \
    GatewayInfo.objects.filter(name=name).count()==0, FieldError("name",'目录名不能和现有网关/目录重复。')
    try:
        assert len(code) == 20
        int(code)
    except:
        raise FieldError("code","国标编码必须是20位长度的数字")
    assert CustomSubDir.objects.filter(dir_code_id=code).count() == 0 and \
           GatewayInfo.objects.filter(code=code).count() == 0, FieldError("code", '国标编码不能和现有网关/目录重复。')
    assert re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip), FieldError('ip', 'ip地址格式错误')
    assert re.match(r"^\d{1,5}$",port), FieldError("port","端口格式错误！必须是int")
    port = int(port)
    limit_ipport = int(limit_ipport)
    assert limit_ipport in (0,1), FieldError("limit_ipport",'limit_ipport可选值是0 1')
    rtp_mode = int(rtp_mode)
    assert rtp_mode in (0, 1), FieldError("rtp_mode",'rtp_mode可选值是 0-udp  1-tcp')
    # is_wandev =
    if dir_code_id == '0'* 20:
        dir_code_id = ''
    assert CustomSubDir.objects.filter(dir_code_id=code).count() == 0 and \
           GatewayInfo.objects.filter(code=code).count() == 0, FieldError("code", '国标编码不能和现有网关/目录重复。')
    if dir_code_id and  dir_code_id != '0' * 20 :
        assert CustomSubDir.objects.filter(dir_code_id=dir_code_id).count() == 1, FieldError("dir_code_id", "父目录不存在！请重试！")
    if dir_code_id == '0'* 20:
        dir_code_id = ''

    _ = GatewayInfo(code=code, name=name, ip=ip, port=port , rtp_mode=rtp_mode,
                    limit_ipport=limit_ipport, addtime=int(time.time()),
                    dir_code_id=dir_code_id)
    _.save()
    return True


@restful_api_deco(login_required=login_required)
def edit_gateway(request):
    # 编辑目录
    post_info = request.POST
    old_code = post_info.get("old_code", "")
    name = post_info.get("name", '').strip()
    code = post_info.get("code", '').strip()
    ip = post_info.get("ip", '').strip()
    port = post_info.get("port", "").strip()
    limit_ipport = post_info.get("limit_ipport", "0").strip()
    # is_wandev = post_info.get("is_wandev", "").strip()
    rtp_mode = post_info.get("rtp_mode", "").strip()
    assert name, FieldError("name", "目录名不能为空")
    assert CustomSubDir.objects.filter(name=name).count() == 0 and \
           GatewayInfo.objects.filter(~Q(code=old_code),name=name).count() == 0, FieldError("name",
                                                                                            '目录名不能和现有网关/目录重复。')
    try:
        assert len(code) == 20
        int(code)
    except:
        raise FieldError("code", "国标编码必须是20位长度的数字")
    if code != old_code:
        assert CustomSubDir.objects.filter(dir_code_id=code).count() == 0 and \
               GatewayInfo.objects.filter(code=code).count() == 0, FieldError("code", '国标编码不能和现有网关/目录重复。')
    assert re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip), FieldError('ip', 'ip地址格式错误')
    assert re.match(r"^\d{1,5}$", port), FieldError("port", "端口格式错误！必须是int")
    port = int(port)
    limit_ipport = int(limit_ipport)
    assert limit_ipport in (0, 1), FieldError("limit_ipport", 'limit_ipport可选值是0 1')
    rtp_mode = int(rtp_mode)
    assert rtp_mode in (0, 1), FieldError("rtp_mode", 'rtp_mode可选值是 0-udp  1-tcp')
    # is_wandev =
    assert GatewayInfo.objects.filter(code=old_code).count() == 1, FieldError("old_code", '设备已不存在，请刷新后重试')
    _ = GatewayInfo.objects.get(code=old_code)
    _.name = name
    _.ip = ip
    _.port = port
    _.rtp_mode = rtp_mode
    _.limit_ipport = limit_ipport
    _.save()
    _.manufacture = ''
    _.last_msg_time = 0
    _.last_scan_catalog_time = 0
    _.reg_time = 0
    _.heartbeat_time = 0
    _.save()
    # 由于code的改变， 其下属设备也要处理
    if code != old_code:
        DeviceNodeInfo.objects.filter(gateway_code=old_code).delete()
    return True



@restful_api_deco(login_required=login_required)
def del_gateway(request):
    #删除设备
    post_info = request.POST
    code = post_info.get("code")
    DeviceNodeInfo.objects.filter(gateway_code=code).delete()    # 清楚网关下的设备。
    GatewayInfo.objects.filter(code=code).delete()                # 清除网关信息。
    return True


@restful_api_deco(login_required=login_required)
def my_sip_info(request):
    """服务端的sip信息
    返回结果：
    {"status": true, "message": "success",
    "data": {"sip_ip": "192.168.1.93", "sip_port": 5066, "sip_id": "00000000042001000006"},
    "errorCode": null}
    """
    return {"sip_ip": config.SIP_SERVER_IP, "sip_port": config.SIP_SERVER_PORT,
            "sip_id": config.SIP_ID}