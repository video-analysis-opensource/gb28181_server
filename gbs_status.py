# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/4/13
# 所有服务的状态。(包含了sip服务  和 流转发服务  流媒体服务)
import os,sys
import setproctitle
import psutil
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
    os.system("mkdir -p %s" % config.WORK_DIR)
    init = psutil.Process(1)
    uwsgi_config = '''<uwsgi>
    <socket>0.0.0.0:{}</socket>
    <protocol>http</protocol>
    <listen>5000</listen>
    <master>true</master>
    <procname>gbs_web</procname>
    <procname-master>gbs_web</procname-master>
    <lazy-apps>false</lazy-apps>
    <harakiri>10</harakiri>
    <chdir>{}</chdir>
    <module>django_wsgi</module>
    <processes>4</processes>
    <max-requests>1000</max-requests>
    <pidfile>{}/uwsgi_gbs.pid</pidfile>
    <buffer-size>32768</buffer-size>
    <daemonize>{}/uwsgi_gbs.log</daemonize>
    <disable-logging>false</disable-logging>
    <env>DJANGO_SETTINGS_MODULE=gbs_zxiat.settings</env>
</uwsgi>'''.format(config.HTTP_SERVER_PORT, os.path.abspath(os.path.dirname(__file__)),
                   config.WORK_DIR.rstrip("/"),config.WORK_DIR.rstrip("/")
                   )
    with open(os.path.join(config.WORK_DIR, "gbs_web.xml"), "w") as f:
        f.write(uwsgi_config)

    services = ['gbs_web', "gbs_sip_server", "gbs_httpflv_server",
                "gbs_websocket"]
    info = {}
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
    for service in services:
        if service not in info:
            red_print(service,'已停止！')
        else:
            green_print(service, "正在运行,共{}个进程".format(len(info[service])))
