# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/4/13
# 启动所有服务。(包含了sip服务  和 流转发服务  流媒体服务)
import os,sys
import setproctitle
import psutil
import time, datetime
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_PATH)
sys.path.append(os.path.join(os.path.dirname(BASE_PATH)))
import config

def green_print(*msg):
    for _ in msg:
        print('\033[92m%s \033[0m' % _,end=' ')
    print('')


def red_print(*msg):
    for _ in msg:
        print('\033[91m%s \033[0m' % _, end=' ')
    print('')


def yellow_print(*msg):
    for _ in msg:
        print('\033[93m%s \033[0m' % _, end=' ')
    print('')


if __name__ == '__main__':
    os.system("sysctl -w net.core.somaxconn=10240")
    os.system("setenforce 0")
    os.system("ulimit -n 10240")
    init = psutil.Process(1)
    services = ["gbs_forward_server"]
    info = {}
    yellow_print("获取服务状态...")
    for p in init.children(True):
        try:
            p_name = p.name()
            p_cmdline = " ".join(p.cmdline()).strip()
        except:
            pass
        else:
            if p_name.startswith("gbs_") :
                if 'gbs_httpflv ' in p_name:
                    info.setdefault("gbs_httpflv_server", [])
                    info['gbs_httpflv_server'].append(p)
                else:
                    info.setdefault(p_name, [])
                    info[p_name].append(p)
            elif ("uwsgi" in p_name and p_cmdline.startswith("gbs_")):
                info.setdefault(p_cmdline, [])
                info[p_cmdline].append(p)

    # print(info)
    already_run = False
    for service in services:
        if service not in info:
            red_print(service,'已停止！')
        else:
            green_print(service, "正在运行,共{}个进程".format(len(info[service])))
            already_run = True
    if already_run:
        yellow_print("尝试停止服务..")
        for service in services:
            if service not in info:
                #red_print(service,'停止..')
                pass
            else:
                #green_print(service, "正在运行,共{}个进程".format(len(info[service])))
                #already_run = True
                for p in info[service]:
                    # print(p)
                    try:
                        p.send_signal(9)
                        p.kill()
                        # p.kill(9)
                        p.wait()
                    except Exception as e:
                        print(str(e))
                        pass
        yellow_print("各服务已停止....")