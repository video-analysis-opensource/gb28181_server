# coding:utf-8
__author__ = "zhou"
# create by zhou on 2021/6/11
import time
from gevent.monkey import patch_all;patch_all()
from gevent.pywsgi import WSGIServer
from flask import Flask, request, render_template,Response
import gevent
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
from collections import OrderedDict
from gevent.server import StreamServer
import json
import socket
import sys
import os, copy
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_PATH)
sys.path.append(os.path.join(os.path.dirname(BASE_PATH)))
import config
try:
    import xmltodict,orm_tool, color_print, get_logger, daemon
except:
    from . import xmltodict,orm_tool, color_print, get_logger, daemon
from gevent.threading import Thread
import requests
import setproctitle
import logging
import datetime
import importlib

log_dir = os.path.join(config.WORK_DIR, "logs")
os.system("mkdir -p %s" % log_dir)


def print_to_logger(*args):
    file_name = os.path.join(log_dir, f"gb_websocket-{datetime.datetime.now().strftime('%Y%m%d')}.log")
    now = datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds')
    try:
        msg = " ".join([str(i) for i in args ])
        with open(file_name, "a+") as f:
            f.write(f"[{now}: INFO]:{msg}\n")
    except:
        pass


print_to_logger("开始启动服务...")
wss_client_set = set()
socket_client_set = set()


def send_str_to_websocket(info: str):
    try:
        for ws in wss_client_set:
            try:
                ws.send(info)
            except Exception as e:
                print_to_logger("exception", e)
                pass
    except Exception as _e:
        print_to_logger("send_str_to_websocket error", str(_e))


def database_read_thread():
    # 读取关键配置，写入到全局变量中
    models = None
    # 建立连接
    while 1:
        # time.sleep(1)
        try:
            models = orm_tool.init_orm()
            break
        except Exception as e:
            print_to_logger("orm init failed", str(e))
            time.sleep(1)
        else:
            print_to_logger("orm init success")
    from django.db import connection
    from django.forms import model_to_dict
    while 1:
        importlib.reload(config)
        hooks = getattr(config, "CAMERA_LIST_HOOKS", [])
        hooks = [i for i in hooks if str(i).startswith("http://")]
        try:
            # 读取所有的设备接入信息
            # 获取某目录下的目录树
            result = []
            # 把所有CustomSubDir信息写入到result中并排序
            infos = {i.dir_code_id: i for i in models.CustomSubDir.objects.all()}
            for a in infos.values():
                result.append({"id": a.dir_code_id,
                               "name": a.name,
                               "parent": a.parent_id or "00000000000000000000",
                               "total_num": 0, "online_num": 0
                               # 'pId':a.parent_id or "00000000000000000000"
                               })
            result.sort(key=lambda x: x['parent'])
            # 真正的结果变量
            final_result = [{"id": "00000000000000000000", "name": "本域", "parent": None, "is_dir": True,
                             "total_num":0, "online_num":0 }]
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
            gateway_info = models.GatewayInfo.objects.all()
            # 查出所有网关信息，并把其放入到final_result
            for i in gateway_info:
                if not i.dir_code_id.strip():
                    final_result.append({"id": i.code, "name": i.name,
                                         "parent": '00000000000000000000', "is_dir": True,
                                         "total_num": 0, "online_num": 0,
                                         'is_gateway': True,
                                         "gateway_code": i.code})
                else:
                    if i.dir_code_id and i.dir_code_id in ids and i.code not in ids:
                        final_result.append({"id": i.code, "name": i.name,
                                             "parent": str(i.dir_code_id), "is_dir": True,
                                             "total_num": 0, "online_num": 0,
                                             'is_gateway': True,
                                             "gateway_code": i.code})
            sub_dir_info = models.DeviceNodeInfo.objects.filter(gateway_code__in=[i.code for i in gateway_info],
                                                                is_dir=1,
                                                                update_time__gt=time.time() - 800)
            _ = {(i.gateway_code, i.code) for i in sub_dir_info}
            for i in sub_dir_info:
                # print(i, i.name, i.parent_node_id, i.gateway_code)
                if (i.gateway_code, i.parent_node_id) in _:
                    final_result.append({"id": i.id,
                                         "name": i.name,
                                         "parent": i.parent_id,
                                         "is_dir": True,
                                         "gateway_code": i.gateway_code,
                                         "total_num":0, "online_num":0 })
                else:
                    if i.parent_node_id == i.gateway_code or i.parent_node_id == '':
                        final_result.append({"id": i.id,
                                             "name": i.name,
                                             "parent": i.parent_id,
                                             "is_dir": True,
                                             "gateway_code": i.gateway_code,
                                             "total_num":0, "online_num":0 })

            _buff = {i["id"]:i for i in final_result}
            # 查询所有的通道信息
            #all_channels = []
            all_channel = models.DeviceNodeInfo.objects.filter(update_time__gt=time.time() - 800, is_dir=0).\
                values("code", "gateway_code", "parent_node_id", 'is_online', "lng", "lat", "name", "ptz_type")
            for channel in all_channel:
                if channel["parent_node_id"] == channel["gateway_code"] or channel["parent_node_id"] == '':
                    parent_id = channel["gateway_code"]
                else:
                    parent_id = "{}_{}".format(channel["gateway_code"],
                                               channel['parent_node_id'])
                #print(parent_id)
                is_online = channel["is_online"]
                while 1:
                    try:
                        _buff[parent_id]['total_num'] += 1
                        if is_online:
                            _buff[parent_id]['online_num'] += 1
                        parent_id = _buff[parent_id]["parent"]
                    except:
                        break
            #print_to_logger(final_result)
            send_str_to_websocket(json.dumps({"data": final_result,
                            "msg_type": "dir_tree_info"}))
            send_str_to_websocket(json.dumps({"data": {i["id"]:{"online_num":i['online_num'],
                                                        "total_num": i["total_num"]} for i in final_result},
                                               "msg_type": "dir_tree_online_info"}))
            post_data = []
            for i in all_channel:
                post_data.append({"cam_url": "gb28181://%s/%s" % (i['gateway_code'],i['code']),
                                  'code': i['code'],
                                  'gateway_code': i['gateway_code'],
                                  'online': bool(i['is_online']),
                                  'name': i['name'],
                                  'lng': i['lng'],
                                  'lat': i['lat'],
                                  'ip': '',
                                  'type': int(i['ptz_type'])
                                  })
            with open("/tmp/post_data", "w") as f:
                f.write(json.dumps(post_data, indent=True))
            for hook_url in hooks:
                try:
                    resp = requests.post(hook_url, json=post_data, timeout=4)
                    print_to_logger("post to CAMERA_LIST_HOOK resp", resp)
                    resp.close()
                except Exception as e:
                    print_to_logger("post to CAMERA_LIST_HOOK ", hook_url, str(e))

        except Exception as e:
            print_to_logger(str(e))
            if "gone away" in str(e):
                try:
                    connection.connect()
                except:
                    pass
        time.sleep(2)


app = Flask(__name__)
#log = logging.getLogger('werkzeug')
#log.disabled = True
#app.logger.disabled = True




@app.route('/api/send_to_ws', methods=['POST'])
def send_to_ws():
    # 发送text到所有的websocket客户端
    data = {"status": True, 'message': 'success'}
    if request.method == 'POST':
        info = request.form.get('info', '') or request.get_data()
        if info:
            for ws in wss_client_set:
                #print(dir(ws))
                try:
                    ws.send(info)
                    #ws.send_frame
                except:
                    pass
        else:
            data['status'] = False
            data['message'] = 'post中，必须包含info信息。或者请求的body中不为空'
    else:
        data['status'] = False
        data['message'] = '调用形式必须是post'

    res = json.dumps(data)
    return Response(res, mimetype='application/json')


class EchoApplication(WebSocketApplication):
    def on_open(self,*args, **kwargs):
        global wss_client_set
        #print("WSS Connection opened", self.ws)
        wss_client_set.add(self.ws)

    def on_message(self, message,*args,**kwargs):
        #print([message, args,kwargs,type(message)])
        #print([message])
        if message == None:
            pass
        else:
            #print(message, args, kwargs)
            if isinstance(message, str):
                self.ws.send(message)
        sys.stdout.flush()

    def on_close(self, reason):
        #print("WSS Connection closed",reason)
        try:
            wss_client_set.remove(self.ws)
        except:
            pass


if __name__ == '__main__':
    argv = sys.argv
    setproctitle.setproctitle("gbs_websocket")
    daemon.redirect_output(os.path.join(config.WORK_DIR, "deamon.out"))
    if argv[-1] == 'daemon':
        daemon.daemon_start()
    p1 = Thread(target=database_read_thread, daemon=True)
    p1.start()
    #http_server = WSGIServer(('0.0.0.0', config.HTTP_WEBSOCKET_API_PORT), app,
    #                         log=log_obj) #  http接口
    #http_server.start()
    WebSocketServer(('0.0.0.0', config.HTTP_WEBSOCKET_PORT),
        Resource(OrderedDict([('/ws/', EchoApplication)]))
    ).serve_forever()
    # websocket
    #socket_server = StreamServer(('0.0.0.0',8005), socket_main)
    #socket_server.serve_forever()
