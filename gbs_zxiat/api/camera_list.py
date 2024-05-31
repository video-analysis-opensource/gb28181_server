# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/5/25
from ..decorators import restful_api_deco,FieldError
from ..models import *
import copy
from django.forms.models import model_to_dict
from django.db.models import Q
import time,datetime
import re
from django.conf import settings
from django.core.paginator import Paginator,InvalidPage

login_required = False

@restful_api_deco(login_required=login_required)
def dir_tree_info(request):
    # 获取目录树
    '''
    获取目录树
    不传参数时， 返回所有的目录树
    传递parent_id 时， 只返回该parent_id 下的目录。
    返回结果示例：
    {
    "status": true,
    "message": "success",
    "data": [
        {
            "id": "11111111110000000007",
            "name": "12225",
            "parent": "00000000000000000000",
            "is_dir": true
        },
        {
            "id": "23324354354655767868",
            "name": "测试",
            "parent": "00000000000000000000",
            "is_dir": true
        }
    ],
    "errorCode": null
}
    '''
    parent_id = request.POST.get("parent_id") or ''
    result = []
    # 把所有CustomSubDir信息写入到result中并排序
    infos = {i.dir_code_id: i for i in CustomSubDir.objects.all()}
    for a in infos.values():
        result.append({"id": a.dir_code_id,
                       "name": a.name,
                       "parent": a.parent_id or "00000000000000000000",
                       # 'pId':a.parent_id or "00000000000000000000"
                       })
    result.sort(key=lambda x: x['parent'])
    # 真正的结果变量
    final_result = [{"id": "00000000000000000000", "name": "本域", "parent": None, "is_dir": True}]
    # 结果筛选， 并append到 final_result中
    # print(result)
    for index_, i in enumerate(copy.deepcopy(result)):
        # print(i["parent"])
        if i["parent"] != '00000000000000000000' and i['parent'] not in infos:
            pass
        else:
            i["is_dir"] = True
            final_result.append(i)
    # 临时存所有的目录id。
    ids = [i["id"] for i in final_result]
    gateway_info = GatewayInfo.objects.all()
    # 查出所有网关信息，并把其放入到final_result
    for i in gateway_info:
        if not i.dir_code_id.strip():
            final_result.append({"id": i.code, "name": i.name, "parent": '00000000000000000000', "is_dir": True,
                                 'is_gateway':True})
        else:
            if i.dir_code_id and i.dir_code_id in ids and i.code not in ids:
                final_result.append({"id": i.code, "name": i.name,
                                     "parent": str(i.dir_code_id), "is_dir": True,
                                     'is_gateway':True,
                                     "gateway_code": i.code})
    sub_dir_info = DeviceNodeInfo.objects.filter(gateway_code__in=[i.code  for i in gateway_info], is_dir=1,
                                                 update_time__gt=time.time() - 800)
    _ = {(i.gateway_code,i.code)  for i in sub_dir_info}
    for i in sub_dir_info:
        print(i,i.name,i.parent_node_id,i.gateway_code)
        if (i.gateway_code, i.parent_node_id) in _:
            final_result.append({"id": i.id,
                                 "name":i.name,
                                 "parent": i.parent_id,
                                 "is_dir":True,
                                 "gateway_code": i.gateway_code})
        else:
            if i.parent_node_id == i.gateway_code or i.parent_node_id == ''  :
                final_result.append({"id": i.id,
                                     "name": i.name,
                                     "parent": i.parent_id,
                                     "is_dir": True,
                                     "gateway_code": i.gateway_code})
    if parent_id:
        final_result = [i  for i in final_result  if i["parent"] == parent_id]
    return final_result


@restful_api_deco(login_required=login_required)
def query_camera_list(request):
    '''
    获取摄像头列表
    支持通过parent_id 查询  或者 name 查询。
    参数说明：
    parent_id   父id
    name       摄像头名。 (其和parent_id 只能二选一)
    page       页数。 默认值是1
    per_page     获取条目数量。 其用于和page参数配合完成分页。默认值是200。
    返回结果示例：
    ptz_type 的对应值：  {'0': '未知', '1': '球机', '2':'半球', '3':'固定枪机', '4':'遥控枪机'}
    {
    "status": true,
    "message": "success",
    "data": {
        "total_num": 10,  # 符合查询条件的总数
        "data": [    # 当前页的数据
            {
                "id": "44010200492000000120_34020000001310000002",
                "name": "IP:192.168.1.177 -球机",
                "ptz_type": "1",
                'ptz_type_cn': '枪机',
                "lng": "0.0",
                "lat": "0.0",
                "manufacture": "Dahua",
                "online": true,
                "httpflv_url": "http://192.168.1.93:8006/?cam_url=gb28181%3A//44010200492000000120/34020000001310000002",
                "wsflv_url": "ws://192.168.1.93:8006/?cam_url=gb28181%3A//44010200492000000120/34020000001310000002",
                "cam_url": "gb28181://44010200492000000120/34020000001310000002"
            },
            ...
        ],
        "total_page": 1,   # 总页数
        "per_page": 200    # 每页数量
    },
    "errorCode": null
}

    '''
    post_info = request.POST
    parent_id = post_info.get("parent_id", '')
    name = post_info.get("name", '')
    page = post_info.get("page", '') or '1'
    page = int(page)
    per_page = post_info.get("per_page", '') or '200'
    #offset = (page - 1) * per_page
    #limit = int(limit)

    result = []
    _ = []
    if parent_id:
        if "_" in parent_id:
            gateway_id, parent_node_id = parent_id.split("_")
            _ = DeviceNodeInfo.objects.filter(gateway_code=gateway_id, parent_node_id=parent_node_id, is_dir=0,
                                              update_time__gt=time.time() - 800)
        else:
            _ = DeviceNodeInfo.objects.filter(gateway_code=parent_id, parent_node_id='', is_dir=0,
                                              update_time__gt=time.time() - 800)
    if name:
        gateway_info = GatewayInfo.objects.all()
        gateway_ids = [i.code  for i in gateway_info]
        _ = DeviceNodeInfo.objects.filter(name__contains=name, gateway_code__in=gateway_ids, is_dir=0,
                                          update_time__gt=time.time() - 800)
    page_obj = Paginator(_,per_page=per_page)
    try:
        info = page_obj.page(page)
    except InvalidPage:
        # info = page_obj.page(1)
        info = []
    for i in info:
        result.append({
            "id": i.id,
            'name': i.name,
            'ptz_type': i.ptz_type,
            'ptz_type_cn': i.ptz_type_cn,
            'lng': i.lng,
            'lat': i.lat,
            'manufacture': i.manufacture,
            'online': i.online,
            'httpflv_url': i.httpflv_url,
            'wsflv_url': i.wsflv_url,
            'cam_url': i.cam_url
        })
    return {"total_num": page_obj.count if _ else 0,
            "data": result,
            "total_page": page_obj.num_pages,
            'per_page': page_obj.per_page }



@restful_api_deco(login_required=login_required)
def get_camera_detail(request):
    '''
    获取摄像头详细信息.
    页面中需要展示：
    摄像头编码：   对应字段是code
    摄像头类型：   ptz_type_cn
    流媒体地址:    httpflv_url
    CAM_URL:     cam_url
    名称：        name
    制造商：       manufacture
    型号：        model
    地址：        address
    经度：         lng
    维度：         lat
    是否在线：      online    是布尔值
    更新时间：      update_time(是以秒为单位的时间戳)

    POST
    参数：
    id  摄像头id
    返回值说明：

    :param request:
    :return:
    '''
    post_info = request.POST
    id = post_info.get("id")
    gateway_id, dev_id = id.split("_")
    node = DeviceNodeInfo.objects.get(gateway_code=gateway_id, code=dev_id)
    node_info = model_to_dict(node)
    del node_info['is_online']
    node_info['id'] = node.id
    node_info['httpflv_url'] = node.httpflv_url
    node_info['cam_url'] = node.cam_url
    node_info['online'] = node.online
    node_info['ptz_type'] = node.ptz_type
    node_info['ptz_type_cn'] = node.ptz_type_cn

    return (node_info)

