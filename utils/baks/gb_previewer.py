# coding:utf-8
__author__ = "zkp"
# create by zkp on 2021/12/8
import bitstring
from gevent.monkey import patch_all;patch_all(thread=False,subprocess=False)
from multiprocessing import Process, Pool
import gevent
import traceback
from gevent.server import DatagramServer
from gevent.pywsgi import WSGIServer
import redis, time
import json
import functools
import cv2, av
import requests
import datetime
import random
import socket
import copy
import urllib.parse
import setproctitle
import sys,os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
try:
    from .gb_decoder_client import RTPDecoderClient, TCPRTPDecoderClient
except:
    from gb_decoder_client import RTPDecoderClient, TCPRTPDecoderClient




def main(local_ip, redis_url):
    import psutil
    _addrs = psutil.net_if_addrs()
    if not local_ip:
        raise Exception('必须给定一个绑定IP参数')
    if not redis_url.startswith("redis"):
        raise  Exception('redis url参数错误')
    addrs = []
    for _ in _addrs.values():
        for j in _:
            if str(j.family) == 'AddressFamily.AF_INET':
                # print(j.family)
                addrs.append(j.address)
    if local_ip not in addrs:
        raise Exception("必须指定一个IP，其可选值是 " + ' '.join(addrs))

    def detect_one_port(start_port=45000, mode='UDP'):
        assert mode in ("TCP", 'UDP')
        gevent.sleep(random.random() / 3)
        if mode == 'TCP':
            flag = socket.SOCK_STREAM
        else:
            flag = socket.SOCK_DGRAM
        for i in range(start_port + random.randrange(0, 5000, 10), 55000, 2):
            try:
                s = socket.socket(socket.AF_INET, flag)
                s.bind(('0.0.0.0', i))
                s1 = socket.socket(socket.AF_INET, flag)
                s1.bind(('0.0.0.0', i + 1))
                s.close()
                s1.close()
            except:
                try:
                    s.close()
                except:
                    pass
                try:
                    s1.close()
                except:
                    pass
            else:
                return i

    def get_device_image(monitor_list:list):
        redis_conn = redis.Redis.from_url(redis_url)
        while 1:
            if len(monitor_list) >= 1:
                device_info = monitor_list[0]
                if device_info.startswith("gb28181://"):
                    # 把尝试获取图片的时间戳写入redis
                    for _try in range(3):
                        # 一共尝试3次
                        url_obj = urllib.parse.urlparse(device_info)
                        mode = 'UDP'
                        try:
                            mode_conf = \
                            requests.get("http://127.0.0.1:8000/api/get_gb_gateway_invite_conf", timeout=3).json()[
                                'data']
                            mode = mode_conf[url_obj.netloc]
                        except:
                            pass
                        print("MODE", device_info, mode)
                        port = detect_one_port(mode=mode)
                        print("try_get image",device_info, port)
                        image_info = ''
                        try:
                            redis_conn.hset("gb_gateway_devices_previewer", "%s_trytime" % device_info, str(int(time.time())))
                            if mode == 'UDP':
                                sip_server = RTPDecoderClient(':' + str(port), only_keyframe=True, image_num=1)
                            else:
                                sip_server = TCPRTPDecoderClient(':' + str(port), only_keyframe=True, image_num=1)
                            sip_server.start_serv()
                            print(mode,"server_start", port)
                            gb_gateway_addr,device_id = device_info[10:].split("/")
                            resp = requests.post("http://127.0.0.1:8000/api/invite_camera", data={'cam_url': device_info,
                                                                                           #'device_id':  device_id,
                                                                                           'play_ip': local_ip,
                                                                                           'play_port': port,
                                                                                            'mode': mode},
                                          timeout=3).json()
                            print(resp)
                            call_id = resp['data']
                            assert call_id
                            sip_server.wait_image()
                            _last_frame = sip_server.last_frame
                            if _last_frame is not None:
                                image_info = bytes(cv2.imencode(".jpg", _last_frame)[1])
                            else:
                                image_info =  ''
                            print("image_info", len(image_info), time.time(), device_info)
                            # 把图片相关信息写入redis
                            if image_info:
                                print("gb_gateway_devices_previewer", "%s_imagecontent" % device_info)
                                redis_conn.hset("gb_gateway_devices_previewer",
                                                "%s_imagecontent" % device_info, image_info)
                                redis_conn.hset("gb_gateway_devices_previewer",
                                                "%s_imagetime" % device_info, str(int(time.time())))
                                #del image_info
                            resp = requests.post("http://127.0.0.1:8000/api/cancel_invite_camera",
                                                 data={'cam_url': device_info,
                                                       'play_ip': local_ip,
                                                       'play_port': port,
                                                       'call_id': call_id},
                                                 timeout=3).json()
                            print('cancel_invite_camera', device_id, resp)
                            sip_server.stop_serv()
                            gevent.sleep(3)
                            del sip_server
                        except Exception as e:
                            print(device_info, "get_device_image exception", str(e)),traceback.print_exc()
                        finally:
                            if image_info:
                                monitor_list.pop(0)
                                break
                            del image_info
                            try:
                                sip_server.stop_serv()
                                del  sip_server
                            except:
                                pass
                    else:
                        try:
                            monitor_list.pop(0)
                        except:
                            pass

            else:
                gevent.sleep(0.5)


    monitor_list_0 = []
    monitor_list_1 = []
    monitor_list_2 = []
    monitor_list_3 = []
    monitor_list_4 = []
    monitor_list_5 = []
    monitor_list_6 = []
    monitor_list_7 = []
    monitor_list_8 = []
    monitor_list_9 = []
    gevent.spawn(get_device_image,monitor_list_0)
    gevent.spawn(get_device_image, monitor_list_1)
    gevent.spawn(get_device_image, monitor_list_2)
    gevent.spawn(get_device_image, monitor_list_3)
    gevent.spawn(get_device_image, monitor_list_4)
    gevent.spawn(get_device_image, monitor_list_5)
    gevent.spawn(get_device_image, monitor_list_6)
    gevent.spawn(get_device_image, monitor_list_7)
    gevent.spawn(get_device_image, monitor_list_8)
    gevent.spawn(get_device_image, monitor_list_9)
    common_list = [monitor_list_0, monitor_list_1, monitor_list_2,monitor_list_3, monitor_list_4, monitor_list_5,
                   monitor_list_6]
    vip_list = [monitor_list_6, monitor_list_7, monitor_list_8, monitor_list_9]


    def monitor_devlist():
        # 监控所有的设备列表， 把其放入到 monitor_list_* 列表中
        redis_conn = redis.Redis.from_url(redis_url)
        while 1:
            gevent.sleep(2)
            try:
                device_info = requests.get("http://127.0.0.1:8000/api/get_camera_list",
                                           timeout=3).json()['data']
                assert  isinstance(device_info, list)
                device_urls = [i['cam_url'] for i in device_info]
            except Exception as e:
                print(str(e))
                pass
            else:
                # print(device_urls)
                try:
                    _ = redis_conn.hmget('gb_gateway_devices_previewer',
                                                    ["%s_trytime" % i for i in device_urls])
                except:
                    pass
                else:
                    trytime_info = []
                    for i in _:
                        try:
                            i = int(i)
                        except:
                            i = 0
                        trytime_info.append(i)
                    trytime_info = list(zip(device_urls, trytime_info))
                    trytime_info.sort(key=lambda x:x[1])
                    for device_url, trytime in trytime_info[:10]:
                        if time.time() - trytime >= 3600*24: # 超过24个小时
                            if trytime != -1:
                                # 发现一个需要放入刷新截图的队列中的 device_url
                                if 16 >= datetime.datetime.now().hour >= 8:
                                    # 只在早8点 到 下午 4点59 进行处理，超过此时段摄像头太黑。
                                    for _list  in common_list:
                                        if len(_list) == 0:
                                            print(device_url,'放入', _list)
                                            _list.append(device_url)
                                            break
                            else:
                                for _list in vip_list:
                                    if len(_list) == 0:
                                        print(device_url, '放入', _list)
                                        _list.append(device_url)
                                        break

    gevent.spawn(monitor_devlist)

    # 循环
    while 1:
        gevent.sleep(0.1)
        sys.stdout.flush()


if __name__ == '__main__':
    local_ip, redis_url = sys.argv[-2:]
    try:
        from . import daemon
    except:
        pass
    import daemon
    daemon.daemon_start()
    print(local_ip, redis_url)
    setproctitle.setproctitle("gb_previewer")
    main(local_ip, redis_url)
