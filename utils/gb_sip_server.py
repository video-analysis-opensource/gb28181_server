# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/4/20
# sip 服务器
from gevent.monkey import patch_all;patch_all(thread=True)
import gevent,traceback
from gevent.pool import Pool as GeventPool
from gevent.server import DatagramServer, StreamServer
import re,random,os,sys,string,time,gzip,datetime,redis,json, pickle, itertools
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_PATH)
sys.path.append(os.path.join(os.path.dirname(BASE_PATH)))
import config
try:
    import xmltodict,color_print, get_logger, daemon, request_utils
except:
    from . import xmltodict,color_print, get_logger, daemon, request_utils
import setproctitle
from gevent.threading import Thread
from gevent.queue import Queue
from sysv_ipc import *
from urllib import parse
import time,requests
import re
import hashlib, copy


setproctitle.setproctitle("gbs_sip_server")


def md5(_str:str):
    return hashlib.md5(_str.encode('utf-8')).hexdigest()

def md5_int(_str: str):
    _ = hashlib.md5(_str.encode('utf-8')).hexdigest()
    return int(_, 16)


os.system("mkdir -p %s" % config.WORK_DIR)
sip_work_dir = os.path.join(config.WORK_DIR, "sip_server")
log_dir = os.path.join(config.WORK_DIR, "logs")
os.system("mkdir -p %s" % sip_work_dir)
os.system("mkdir -p %s" % log_dir)
os.system("mkdir -p /tmp/gbs_zxiat")
redis_url = config.REDIS_URL

def print_to_logger(*args):
    file_name = os.path.join(log_dir, f"gb_sip_server-{datetime.datetime.now().strftime('%Y%m%d-%H')}.log")
    now = datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds')
    try:
        msg = " ".join([str(i) for i in args ])
        with open(file_name, "a+") as f:
            f.write(f"[{now}: INFO]:{msg}\n")
    except:
        pass

print_to_logger("开始启动服务...")
# sip server专用：
my_sip_id = config.SIP_ID                       # sip 设备id
sip_server_ip = config.SIP_SERVER_IP            # 本机IP， 根据需要更改
sip_server_port = str(config.SIP_SERVER_PORT)    # sip端口  - 下级设备接入
sip_server_contact_router = config.SIP_SERVER_CONTACT_ROUTER # sip contact router
# sip api 服务：
sip_api_port = str(config.SIP_SERVER_API_PORT)  # sip api


# catalog查询间隔
CATALOG_CHECK_DURATION = 300

# my pid
my_pid = os.getpid()
# 多进程消息队列
msg_handle_queue = Queue(maxsize=50000)


def msg_handle_function():
    # 消息处理逻辑
    # orm初始化
    print_to_logger('msg_handle_function')
    # 获取队列中的消息
    while 1:
        try:
            info = msg_handle_queue.get_nowait()
            requests.post("http://127.0.0.1:%s/data_handle/" % config.HTTP_SERVER_PORT,
                                 data=info)
        except Exception as e:
            print(str(e))
            gevent.sleep(0.01)
        else:
            pass


# 国标接入信息
gb_gateways = {}

# 国标设备信息
gb_devs = {}


def database_read_thread():
    # 读取关键配置，写入到全局变量中
    global gb_gateways, gb_devs
    while 1:
        # 获取接入的设备信息 写入到全局变量
        try:
            gb_gateways, gb_devs = requests.get("http://127.0.0.1:%s/gb_gateway_devs/" % config.HTTP_SERVER_PORT).json()
            print_to_logger("requests get gb_devs success!", gb_gateways)
        except Exception as e:
            print_to_logger("requests get gb_devs err!", str(e))
        gevent.sleep(1.5)


# 信令服务器USER AGENT
USER_AGENT = 'GBS_ZXIAT_sipserver'


class AutoSharedMemory(object):
    # 带自动过期功能的共享内存
    # 基于sysv_ipc库
    def __init__(self, expires: int = 150, size=100):
        self.expires = expires
        self._shared_mems = {}
        self.size = size

    @classmethod
    def md5_8(cls, string: str) -> str:
        return hashlib.md5(string.encode('utf-8')).hexdigest()[-8:]

    def read_mem_bytes(self, mem_obj) -> bytes:
        return mem_obj.read().rstrip(b"\x00")

    def write_mem_bytes(self, mem_obj, bytes_content: bytes):
        _len = len(bytes_content)
        mem_obj.write(bytes_content + (self.size - _len) * b"\x00")

    def _get_mem_obj(self, key: str):
        _id = int(self.md5_8(string=key), 16)
        if key not in self._shared_mems:
            self._shared_mems[key] = SharedMemory(_id, flags=IPC_CREAT,
                                                  size=self.size)
        return self._shared_mems[key]

    def set(self, key: str, v):
        '设置key'
        mem_obj = self._get_mem_obj(key)
        _ = pickle.dumps((v, time.time()))
        self.write_mem_bytes(mem_obj, _)

    def get(self, key: str):
        '读取key'
        mem_obj = self._get_mem_obj(key)
        info = self.read_mem_bytes(mem_obj)
        # print(info,len(info),type(info))
        if info:
            _ = pickle.loads(info)
            v, _t = _
            if time.time() - _t < self.expires:
                return v
        return None

    def remove(self, key: str):
        '删除 key'
        mem_obj = self._get_mem_obj(key)
        self.write_mem_bytes(mem_obj, b"\x00" * self.size)


class SipServer(DatagramServer):
    "信令服务器"

    def __init__(self, *args, sip_id, sip_ip, sip_port, contact_route, **kwargs):
        DatagramServer.__init__(self, *args, **kwargs)
        # 在线的server缓存。 如果超过150秒 就认为离线。
        # 客户端的心跳时间最好设置为30秒
        self.conn_shared_info = AutoSharedMemory(expires=150, size=300)
        self.contact_route = contact_route
        self.sip_id = sip_id
        self.sip_ip = sip_ip
        self.sip_port = sip_port

    def gen_contact(self, dev_id):
        "生成contact"
        return 'Contact: <sip:{}@{}:{}>\r\n'.format(self.sip_id,self.get_contact_ip(dev_id), self.sip_port)

    def get_contact_ip(self, dev_id):
        return self.contact_route.get(dev_id) or self.contact_route.get("default") or config.SIP_SERVER_IP

    def send_sip_content(self, gateway_id, content:str):
        "发送sip信令"
        #print(gateway_id, content, gb_gateways)
        if gateway_id in gb_gateways:
            limit_ipport = gb_gateways[gateway_id]['limit_ipport']
            limit_ip, limit_port = gb_gateways[gateway_id]["ip"], gb_gateways[gateway_id]["port"]
            try:
                ip, port = self.conn_shared_info.get(str(gateway_id))[:2]
                print_to_logger(ip, port, limit_ip, limit_port, limit_ipport)
            except Exception as e:
                print_to_logger("Error! gateway", gateway_id, "not connected! ")
            else:
                if limit_ipport:
                    if ip == limit_ip and port == limit_port:
                        print_to_logger("xxx",ip, port, content)
                        self.socket.sendto(content.encode('gbk'), (ip, port))
                    else:
                        print_to_logger(gateway_id,"{}:{}非法，其必须是{}:{}".format(ip, port, limit_ip, limit_port))
                else:
                    print_to_logger("xxx", ip, port, content)
                    self.socket.sendto(content.encode('gbk'), (ip, port))
        else:
            print_to_logger(gateway_id, "是非法的设备,不允许接入！")


    def send_content_to(self, content:str, to):
        "发送sip信息到指定地址"
        self.socket.sendto(content.encode('gbk'), to)

    def parse_sip_msg(self, content: bytes):
        # 对SIP消息进行解析
        # 返回一个元组
        #  (type, header, content, is_request, url)
        #  type。 如： INVITE  MESSAGE  REGISTER      200 OK
        #  header  请求头/返回头
        #  是否是请求。True or False
        #  url   请求URL
        content = content.decode('gbk')
        if "\r\n" in content[:400]:
            mark = "\r\n\r\n"
        else:
            mark = '\n\n'
            # 按照\r\n换行
        try:
            if content.startswith("SIP/"):
                _type = re.match("SIP/[^ ]+ +(\d+.+)", content[:120]).groups()[0].strip()
                _type = " ".join(_type.split())
                is_request = False
                url = None
            else:
                is_request = True
                _type, url = content.split(" ")[:2]
                # _type = content[:_]
                # url =
            # if _type.isupper():
            _ = content.find(mark)
            head_content = content[:_]
            header = {}
            # 兼容多Via 的格式
            for i,j in [[j.strip() for j in i.split(": ", 1)] for i in head_content.splitlines()[1:]]:
                if i not in header:
                    header[i] = j
                else:
                    old_val = header[i]
                    if isinstance(old_val, str):
                        header[i] = [old_val, j]
                    else:
                        old_val.append(j)
            if is_request:
                from_dev_id = re.search(r"<sip:(\d{20})@",header["From"]).groups()[0]
            else:
                from_dev_id = re.search(r"<sip:/?/?(\d{20})@",header["To"]).groups()[0]
            # print("11",header)
            content = content[_:].strip()
            # if 'Record-Route' in header:
            #     self.route_shared_info.set(from_dev_id, )
            return _type, header, content, is_request, url, from_dev_id
        except Exception as e:
            print_to_logger(str(e))
            print_to_logger(traceback.format_exc())



    def gen_catalog_msg(self, gateway_id, device_id=None):
        nvr_info = "%s@%s" % (gateway_id, gateway_id[:10])
        if not device_id:
            device_id = nvr_info[:nvr_info.find('@')]
        else:
            pass
        list1 = '<?xml version="1.0"?>\n<Query>\n<CmdType>Catalog</CmdType>\n' \
                '<SN>1{}</SN>\n<DeviceID>{}</DeviceID>\n</Query>\n'.format(
            str(random.randint(10000, 99999))[1:], device_id)
        str_send = 'MESSAGE sip:{} SIP/2.0\r\n'.format(nvr_info)
        str_send += 'To: <sip:{}>\r\n'.format(nvr_info)
        str_send += 'Content-Length: {}\r\n'.format(len(list1))
        str_send += 'CSeq: 2 MESSAGE\r\n'
        str_send += 'Call-ID: 12495{}\r\n'.format(str(random.randint(10000, 99999))[1:])
        str_send += 'Via: SIP/2.0/UDP {}:{};branch=z9hG4bK{}\r\n'.format(self.sip_ip,self.sip_port,
                                                              md5(str(random.random()) + str(time.time()))[:25])
        str_send += 'From: <sip:{}@{}:{}>;tag=50048{}\r\n'.format(self.sip_id, self.sip_ip,
                                                                  self.sip_port,
                                                                str(random.randint(10000, 99999))[
                                                                1:])
        str_send += 'Content-Type: Application/MANSCDP+xml\r\n'
        str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        #str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        str_send += 'Max-Forwards: 70\r\n\r\n'
        str_send += list1
        b4 = str_send
        return b4


    def gen_recordinfo_msg(self, gateway_id, device_id):
        nvr_info = "%s@%s" % (gateway_id, gateway_id[:10])
        list1 = '<?xml version="1.0"?>\n<Query>\n<CmdType>RecordInfo</CmdType>\n' \
                '<SN>1{}</SN>\n<DeviceID>{}</DeviceID>\n' \
                '<StartTime>{}</StartTime><EndTime>{}</EndTime><Type>all</Type></Query>\n'.format(
            str(random.randint(10000000, 99999000))[1:], device_id,
            (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S"),
            datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        )
        str_send = 'MESSAGE sip:{} SIP/2.0\r\n'.format(device_id+ '@' + nvr_info.split("@")[1])
        str_send += 'To: <sip:{}>\r\n'.format(device_id+ '@' + nvr_info.split("@")[1])
        str_send += 'Content-Length: {}\r\n'.format(len(list1))
        str_send += 'CSeq: 2 MESSAGE\r\n'
        str_send += 'Call-ID: 12495{}\r\n'.format(str(random.randint(100000000, 999990000))[1:])
        str_send += 'Via: SIP/2.0/UDP {}:{};rport;branch=z9hG4bK{}\r\n'.format(self.sip_ip,self.sip_port,
                                     md5(str(random.random()) + str(time.time()))[:25])
        str_send += 'From: <sip:{}@{}:{}>;tag=50048{}\r\n'.format(self.sip_id, self.sip_ip,
                                                                  self.sip_port,
                                                                  str(random.randint(10000, 99999))[
                                                                  1:])
        str_send += 'Content-Type: Application/MANSCDP+xml\r\n'
        str_send += 'Max-Forwards: 70\r\n\r\n'
        str_send += list1
        b4 = str_send
        return b4


    def gen_invite_msg(self, gateway_id, device_id, play_ip, play_port, mode='UDP'):
        # 生成invite消息
        limit_ip, limit_port = gb_gateways[gateway_id]["ip"], gb_gateways[gateway_id]["port"]
        device_gbgateway = "%s@%s:%s" % (gateway_id, limit_ip, limit_port)
        assert mode in ('UDP', 'TCP')
        y = device_id[2:8] + str(random.randrange(1000,9999))
        if mode == 'UDP':
            list1 = 'v=0\r\n'
            list1 += 'o={} 0 0 IN IP4 {}\r\n'.format(self.sip_id, play_ip)
            list1 += 's=Play\r\n'
            list1 += 'c=IN IP4 {}\r\n'.format(play_ip)
            list1 += 't=0 0\r\n'
            list1 += 'm=video {} RTP/AVP 96 98 97\r\n'.format(play_port)
            #list1 += 'i=primary\r\n'
            list1 += 'a=rtpmap:96 PS/90000\r\n'
            list1 += 'a=rtpmap:98 H264/90000\r\n'
            list1 += 'a=rtpmap:97 MPEG4/90000\r\n'
            list1 += 'a=recvonly\r\n'
            list1 += 'a=streamMode:MAIN\r\n'
            list1 += 'a=filesize:-1\r\n'
            list1 += f'y={y}\r\n'
        elif mode == 'TCP':
            list1 = 'v=0\r\n'
            list1 += 'o={} 0 0 IN IP4 {}\r\n'.format(self.sip_id, play_ip)
            list1 += 's=Play\r\n'
            list1 += 'c=IN IP4 {}\r\n'.format(play_ip)
            list1 += 't=0 0\r\n'
            list1 += 'm=video {} TCP/RTP/AVP 96 98 97\r\n'.format(play_port)
            list1 += 'i=primary\r\n'
            list1 += 'a=rtpmap:96 PS/90000\r\n'
            list1 += 'a=rtpmap:98 H264/90000\r\n'
            list1 += 'a=rtpmap:97 MPEG4/90000\r\n'
            list1 += 'a=streamMode:MAIN\r\n'
            list1 += 'a=setup:passive\r\n'
            list1 += 'a=connection:new\r\n'
            list1 += 'a=recvonly\r\n'
            #list1 += 'a=filesize:-1\r\n'
            list1 += f'y={y}\r\n'

        str_send = 'INVITE sip:{}{} SIP/2.0\r\n'.format(device_id, device_gbgateway[device_gbgateway.find('@'):])
        str_send += 'Via: SIP/2.0/UDP {}:{};branch=z9hG4bK{}\r\n'.format(self.sip_ip, self.sip_port,
                                                                    md5(str(random.random()) + str(time.time()))[:25]
                                                                         )
        str_send += 'From: <sip:{}@{}:{}>;tag={}\r\n'.format(self.sip_id, self.sip_ip, self.sip_port,
                                                             play_ip.replace(".",'') + "XX" + str(play_port)  #+
                                                             #''.join(random.sample(string.ascii_letters,10))
                                                             )
        str_send += 'To: <sip:{}{}>\r\n'.format(device_id, device_gbgateway[device_gbgateway.find('@'):],
                                                       #play_ip.replace(".",'') + "XX" + str(play_port)
                                                )
        str_send += 'Call-ID: {}\r\n'.format(#call_id
            #''.join(random.sample(string.ascii_letters,32))
            # device_id + play_ip.replace(".",'') + "XX" + str(play_port)
            int(hashlib.md5((device_id + play_ip.replace(".", '') +
                             "XX" + str(play_port)).encode()).hexdigest()[:16], 16)
        )
        str_send += 'CSeq: 2 INVITE\r\n'
        str_send += self.gen_contact(gateway_id)
        #str_send += 'Contact: <sip:{}@{}:{}>\r\n'.format(self.sip_id, self.sip_ip, self.sip_port)
        str_send += 'Content-Type: Application/SDP\r\n'
        str_send += 'Max-Forwards: 70\r\n'
        str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        str_send += 'Subject: {}:{},{}:0\r\n'.format(device_id, y, self.sip_id)
        str_send += 'Content-Length: {}\r\n\r\n'.format(len(list1))
        str_send += list1
        return str_send


    def gen_subscribe_msg(self, gateway_id):
        # 生成订阅消息。
        device_gbgateway = "%s@%s" % (gateway_id, gateway_id[:10])
        #device_id = device_gbgateway[:device_gbgateway.find('@')]
        list1 = '<?xml version="1.0"?>\n<Query>\n<CmdType>Catalog</CmdType>\n' \
                '<SN>1{}</SN>\n<DeviceID>{}</DeviceID>\n</Query>\n'.format(
            str(random.randint(10000, 99999))[1:], gateway_id)
        str_send = 'SUBSCRIBE sip:{} SIP/2.0\r\n'.format(device_gbgateway)
        str_send += 'Via: SIP/2.0/UDP {}:{}\r\n'.format(self.sip_ip, self.sip_port,
                                                        # str(random.randint(1000, 9999))
                                                        )
        str_send += 'From: <sip:{}@{}:{}>;tag={}\r\n'.format(self.sip_id, self.sip_ip, self.sip_port,
                                                             # play_ip.replace(".", '') + "XX" + str(play_port)  # +
                                                           ''.join(random.sample(string.ascii_letters,15))
                                                             )
        str_send += 'To: <sip:{}>\r\n'.format(device_gbgateway)
        str_send += 'Call-ID: {}\r\n'.format(
            int(hashlib.md5(device_gbgateway.encode("utf-8")).hexdigest()[:10], 16)
            #call_id
                                           # ''.join(random.sample(string.ascii_letters,32))
                                           # device_id + play_ip.replace(".",'') + "XX" + str(play_port)
                                           )
        str_send += 'CSeq: 1 SUBSCRIBE\r\n'
        str_send += self.gen_contact(gateway_id)
        str_send += 'Content-Type: Application/MANSCDP+xml\r\n'
        str_send += 'Max-Forwards: 70\r\n'
        str_send += 'Event: Catalog\r\n'
        str_send += 'Expires: 600000\r\n'
        str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        str_send += 'Content-Length: {}\r\n\r\n'.format(len(list1))
        return str_send + list1

    def gen_gw_status_msg(self, gateway_id):
        # 生成查询设备在线状态消息
        device_gbgateway = "%s@%s" % (gateway_id, gateway_id[:10])
        #device_id = device_gbgateway[:device_gbgateway.find('@')]
        list1 = '<?xml version="1.0"?>\n<Query>\n<CmdType>DeviceStatus</CmdType>\n' \
                '<SN>1{}</SN>\n<DeviceID>{}</DeviceID>\n</Query>\n'.format(
            str(random.randint(10000, 99999))[1:], gateway_id)
        str_send = 'MESSAGE sip:{} SIP/2.0\r\n'.format(device_gbgateway)
        str_send += 'Via: SIP/2.0/UDP {}:{};branch=z9hG4bK{}\r\n'.format(self.sip_ip, self.sip_port,
                                                                        md5(str(random.random()) + str(time.time()))[:25])
        str_send += 'From: <sip:{}@{}:{}>;tag={}\r\n'.format(self.sip_id, self.sip_ip, self.sip_port,
                                                             # play_ip.replace(".", '') + "XX" + str(play_port)  # +
                                                           ''.join(random.sample(string.ascii_letters, 15))
                                                             )
        str_send += 'To: <sip:{}>\r\n'.format(device_gbgateway)
        str_send += 'Call-ID: {}\r\n'.format(
            #hashlib.md5(device_gbgateway.encode("utf-8")).hexdigest()
            # call_id
            ''.join(random.sample(string.ascii_letters,32))
            # device_id + play_ip.replace(".",'') + "XX" + str(play_port)
        )
        str_send += 'CSeq: 15 MESSAGE\r\n'
        str_send += self.gen_contact(gateway_id)
        str_send += 'Content-Type: Application/MANSCDP+xml\r\n'
        str_send += 'Max-Forwards: 70\r\n'
        str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        str_send += 'Content-Length: {}\r\n\r\n'.format(len(list1))
        return str_send + list1


    def gen_gw_info_msg(self, gateway_id):
        # 生成查询设备信息 消息
        limit_ip, limit_port = gb_gateways[gateway_id]["ip"], gb_gateways[gateway_id]["port"]
        device_gbgateway = "%s@%s:%s" % (gateway_id, limit_ip, limit_port)
        # device_id = device_gbgateway[:device_gbgateway.find('@')]
        list1 = '<?xml version="1.0"?>\n<Query>\n<CmdType>DeviceInfo</CmdType>\n' \
                '<SN>1{}</SN>\n<DeviceID>{}</DeviceID>\n</Query>\n'.format(
            str(random.randint(10000, 99999))[1:], gateway_id)
        str_send = 'MESSAGE sip:{} SIP/2.0\r\n'.format(device_gbgateway)
        str_send += 'Via: SIP/2.0/UDP {}:{};branch=z9hG4bK{}\r\n'.format(self.sip_ip, self.sip_port,
                                                            md5(str(random.random()) + str(time.time()))[:25])
        str_send += 'From: <sip:{}@{}:{}>;tag={}\r\n'.format(self.sip_id, self.sip_ip, self.sip_port,
                                                             # play_ip.replace(".", '') + "XX" + str(play_port)  # +
                                                           ''.join(random.sample(string.ascii_letters, 15))
                                                             )
        str_send += 'To: <sip:{}>\r\n'.format(device_gbgateway)
        str_send += 'Call-ID: {}\r\n'.format(
            #hashlib.md5(device_gbgateway.encode("utf-8")).hexdigest()
            # call_id
            ''.join(random.sample(string.ascii_letters,32))
            # device_id + play_ip.replace(".",'') + "XX" + str(play_port)
        )
        str_send += 'CSeq: 15 MESSAGE\r\n'
        str_send += self.gen_contact(gateway_id)
        #'Contact: <sip:{}@{}:{}>\r\n'.format(my_device_id, local_ip, local_sip_port)
        str_send += 'Content-Type: Application/MANSCDP+xml\r\n'
        str_send += 'Max-Forwards: 70\r\n'
        # str_send += 'Event: Catalog;id=1894\n'
        # str_send += 'Expires: 600000\n'
        str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        str_send += 'Content-Length: {}\r\n\r\n'.format(len(list1))
        return str_send + list1


    def gen_cancel_invite_msg(self, gateway_id, device_id, play_ip, play_port, mode):
        # 生成取消invite消息.
        # 暂时无用
        #device_gbgateway = "%s@%s" % (gateway_id, gateway_id[:10])
        limit_ip, limit_port = gb_gateways[gateway_id]["ip"], gb_gateways[gateway_id]["port"]
        device_gbgateway = "%s@%s:%s" % (gateway_id, limit_ip, limit_port)
        str_send = 'BYE sip:{}@{}:{} SIP/2.0\r\n'.format(device_id, limit_ip, limit_port)
        str_send += 'Via: SIP/2.0/UDP {}:{};branch=z9hG4bK{}\r\n'.format(self.sip_ip, self.sip_port,
                                                    md5(str(random.random()) + str(time.time()))[:25])
        str_send += 'From: <sip:{}@{}:{}>;tag={}\r\n'.format(self.sip_id, self.sip_ip, self.sip_port,
                                                             play_ip.replace(".",'') + "XX" + str(play_port))
        call_id = int(hashlib.md5((device_id + play_ip.replace(".", '') +
                             "XX" + str(play_port)).encode()).hexdigest()[:16], 16)

        play_tag_id = ''
        record_route = None
        try:
            redis_conn = redis.Redis.from_url(redis_url)
            old_tag_info = redis_conn.get("callid_tag_%s" % call_id)
            redis_conn.expire("callid_tag_%s" % call_id, 3600)
            redis_conn.close()
            _tag_info = json.loads(old_tag_info)
            play_tag_id = _tag_info['tag_id']
            record_route = copy.deepcopy(_tag_info.get("Record-Route",None))
        except:
            pass
        # route处理
        if record_route:
            if isinstance(record_route, list):
                record_route.reverse()
                for r in record_route:
                    str_send += 'Route: {}\r\n'.format(r)
            else:
                str_send += 'Route: {}\r\n'.format(record_route)
        if play_tag_id:
            play_tag_id  =  play_tag_id or  (play_ip.replace(".",'') + "XX" + str(play_port))
            #if play_tag_id:
            str_send += 'To: <sip:{}{}>;tag={}\r\n'.format(device_id, device_gbgateway[device_gbgateway.find('@'):],
                                                           play_tag_id)
        else:
            str_send += 'To: <sip:{}{}>\r\n'.format(device_id, device_gbgateway[device_gbgateway.find('@'):])
        # else:
        #     str_send += 'To: <sip:{}{}>\r\n'.format(device_id, device_gbgateway[device_gbgateway.find('@'):],
        #                                                   )

        str_send += 'Call-ID: {}\r\n'.format(
            call_id
            #call_id
        )
        str_send += 'CSeq: 3 BYE\r\n'
        str_send += self.gen_contact(gateway_id)
        str_send += 'Max-Forwards: 70\r\n'
        str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        str_send += 'Content-Length: 0\r\n\r\n'
        return str_send


    def common_resp(self, gateway_id, req_header:dict, type:str='200 OK'):
        # 构造普通响应消息
        try:
            str_send = 'SIP/2.0 %s\r\n' % type
            via = req_header['Via']
            if isinstance(via, str):
                str_send += 'Via: {}\r\n'.format(
                    via
                )
            else:
                for _v in via:
                    str_send += 'Via: {}\r\n'.format(
                        _v
                    )
            str_send += 'From: {}\r\n'.format(req_header['From'])
            str_send += 'To: {}\r\n'.format(req_header['To'])
            str_send += self.gen_contact(gateway_id)
            if 'User-Agent' in req_header:
                str_send += 'User-Agent: {}\r\n'.format(req_header['User-Agent'])
            if 'User-agent' in req_header:
                str_send += 'User-agent: {}\r\n'.format(req_header['User-agent'])
                str_send += 'User-Agent: {}\r\n'.format(req_header['User-agent'])
            if 'Error-Info' in  req_header:
                str_send += 'Error-Info: {}\r\n'.format(req_header['Error-Info'])
            str_send += 'CSeq: {}\r\n'.format(req_header['CSeq'])
            str_send += 'Call-ID: {}\r\n'.format(req_header['Call-ID'])
            str_send += 'Content-Length: 0\r\n\r\n'
            return str_send
        except Exception as e:
            print_to_logger("common_resp", str(e), req_header)
            print_to_logger(traceback.format_exc())


    def invite_ack_success_msg(self, dev_id, req_headers:dict):
        # 构造 invite ack 消息
        limit_ip, limit_port = gb_devs[dev_id]["ip"], gb_devs[dev_id]["port"]
        nvr_info = "%s@%s:%s" % (dev_id, limit_ip, limit_port)
        # nvr_info = "%s@%s" % (gateway_id, gateway_id[:10])  # 设备信息
        tag_info = re.search(r";tag=(.+)",req_headers['From']).groups()[0] # tag信息
        str_send = 'ACK sip:{} SIP/2.0\r\n'.format(nvr_info)
        if isinstance(req_headers['Via'], list):
            via = req_headers['Via'][0]
        else:
            via = req_headers['Via']
        str_send += 'Via: SIP/2.0/UDP {}:{};branch={}\r\n'.format(
            self.sip_ip, self.sip_port,
            via.split(";received")[0].split("branch=")[1])
        # route处理
        record_route = copy.deepcopy(req_headers.get("Record-Route", None))
        if record_route:
            if isinstance(record_route,list):
                record_route.reverse()
                for r in record_route:
                    str_send += 'Route: {}\r\n'.format(r)
            else:
                str_send += 'Route: {}\r\n'.format(record_route)
        str_send += 'From: <sip:{}@{}:{}>;tag={}\r\n'.format(self.sip_id, self.sip_ip ,
                                                             self.sip_port, tag_info)
        to_tag_info = re.findall(r";tag=([^;]+)",req_headers.get('To','')) # to tag信息
        if not to_tag_info:
            str_send += 'To: <sip:{}>\r\n'.format(
                re.match(r"<sip:([^>]+)>", req_headers['To']).groups()[0])
        else:
            str_send += 'To: <sip:{}>;tag={}\r\n'.format(
                re.match(r"<sip:([^>]+)>", req_headers['To']).groups()[0], to_tag_info[-1])
        # str_send += self.gen_contact(gateway_id)
        str_send += 'Contact: <sip:{}@{}:{}>\r\n'.format(self.sip_id, self.sip_ip, self.sip_port)
        str_send += 'CSeq: {}\r\n'.format(
            req_headers['CSeq'].replace("INVITE", "ACK"))
        str_send += 'Call-ID: {}\r\n'.format(
            req_headers['Call-ID'])
        str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        str_send += 'Max-Forwards: 70\r\n'
        str_send += 'Content-Length: 0\r\n\r\n'
        return str_send


    def invite_ack_failed_msg(self, dev_id, req_headers):
        limit_ip, limit_port = gb_devs[dev_id]["ip"], gb_devs[dev_id]["port"]
        nvr_info = "%s@%s:%s" % (dev_id, limit_ip, limit_port)
        #nvr_info = "%s@%s" % (gateway_id, gateway_id[:10])  # 设备信息
        str_send = 'ACK sip:{} SIP/2.0\r\n'.format(nvr_info)
        str_send += 'To: {}\r\n'.format(req_headers['To'])
        str_send += 'Content-Length: 0\r\n'
        str_send += 'CSeq: {}\r\n'.format(
            req_headers['CSeq'].replace("INVITE", "ACK"))
        str_send += 'Call-ID: {}\r\n'.format(
            req_headers['Call-ID'])
        if isinstance(req_headers['Via'], list):
            via = req_headers['Via'][0]
        else:
            via = req_headers['Via']
        str_send += 'Via: SIP/2.0/UDP {}:{};branch={}\r\n'.format(
            self.sip_ip, self.sip_port,
            via.split(";received")[0].split("branch=")[1])
        record_route = req_headers.get("Record-Route", None)
        if record_route:
            if isinstance(record_route, list):
                record_route.reverse()
                for r in record_route:
                    str_send += 'Route: {}\r\n'.format(r)
            else:
                str_send += 'Route: {}\r\n'.format(record_route)
        str_send += 'From: {}\r\n'.format(req_headers['To'])
        str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        str_send += 'Max-Forwards: 70\r\n\r\n'
        return str_send

    def gen_ptz_control_msg(self, gateway_id, device_id, action,  move_speed:int=36, zoom_speed:int=3):
        # 生成ptz控制消息
        limit_ip, limit_port = gb_gateways[gateway_id]["ip"], gb_gateways[gateway_id]["port"]
        device_gbgateway = "%s@%s:%s" % (gateway_id, limit_ip, limit_port)
        # device_gbgateway = "%s@%s" % (gateway_id, gateway_id[:10])
        width_speed = move_speed
        height_speed = move_speed
        zoom_speed = zoom_speed
        assert action in ("left", "right", 'up', 'down',
                          'leftup','leftdown',"rightup", "rightdown",
                          'big', 'small',
                          'stop')
        # _action_dict = {'left': 0x02, 'right':0x01, 'up': 0x04, 'down': 0x08,
        #                 'leftup':0x06, 'leftdown':0x0A, 'rightup':0x05,'rightdown':0x09,
        #                 'big': 0x10, 'small': 0x20, 'stop': 0x00}

        _action_dict = { 'left': 0x02, 'right': 0x01, 'up': 0x08, 'down': 0x04,
                         'leftup': 0x0A, 'leftdown': 0x06, 'rightup': 0x09, 'rightdown': 0x05,
                         'big': 0x10, 'small': 0x20, 'stop': 0x00 }

        action_cmd = _action_dict[action]
        list1 = '<?xml version="1.0"?>\n'
        list1 += '<Control>\r\n'
        list1 += '<CmdType>DeviceControl</CmdType>\r\n'
        list1 += '<SN>{}</SN>\r\n'.format(str(random.randint(100000, 999999))[1:])
        list1 += '<DeviceID>{}</DeviceID>\r\n'.format(device_id)
        list1 += '<PTZCmd>a50f4d{:0>2}{:0>2}{:0>2}{:0>2}{:0>2}</PTZCmd>\r\n'.format(
            hex(action_cmd)[2:],
            hex(height_speed)[2:],
            hex(width_speed)[2:],
            hex(zoom_speed)[2:],
            hex((0xa5 + 0x0f + 0x4d + action_cmd + height_speed + width_speed + zoom_speed) % 0x100)[2:])
        # list1 += '<Info>\r\n'
        # list1 += '<ControlPriority>150</ControlPriority>\r\n'
        # list1 += '<startX>0</startX>\r\n'
        # list1 += '<startY>0</startY>\r\n'
        # list1 += '<endX>0</endX>\r\n'
        # list1 += '<endY>0</endY>\r\n'
        # list1 += '</Info>\r\n'
        list1 += '</Control>\r\n'

        str_send = 'MESSAGE sip:{} SIP/2.0\n'.format(device_gbgateway)
        str_send += 'Via: SIP/2.0/UDP {}:{};branch=z9hG4bK{}\n'.format(self.sip_ip, self.sip_port,
                                                                md5(str(random.random()) + str(time.time()))[:25])
        str_send += 'From: <sip:{}@{}:{}>;tag=500485{}\n'.format(self.sip_id, self.sip_ip, self.sip_port,
                                                                               str(random.randint(1000, 9999)))
        str_send += 'To: <sip:{}{}>\r\n'.format(device_id, device_gbgateway[device_gbgateway.find('@'):])
        str_send += 'Call-ID: PTZ_{}_{}\r\n'.format(action,
                                                       #device_gbgateway,
                                                       ''.join(random.sample(string.ascii_letters + '0123456789', 8)))
        str_send += 'CSeq: 20 MESSAGE\n'
        str_send += 'Content-Type: Application/MANSCDP+xml\n'
        str_send += self.gen_contact(gateway_id)
        str_send += 'Max-Forwards: 70\n'
        str_send += 'User-Agent: {}\r\n'.format(USER_AGENT)
        str_send += 'Content-Length: {}\n\n'.format(len(list1))
        str_send += list1
        return str_send


    def handle(self, data, address):
        # 核心处理逻辑
        try:
            #print_to_logger("raw_data", data)
            req_data = self.parse_sip_msg(data)
            #print("raw_data", data)
            if req_data:
                _type, headers, content, is_request, url, from_dev_id = req_data
                if from_dev_id in gb_gateways:
                    # 读取 源地址写入到共享内存
                    last_catalog_time = 0
                    try:
                        _last_info = self.conn_shared_info.get(from_dev_id)
                        if _last_info:
                            last_catalog_time = int(_last_info[-1])
                        if not _last_info:
                            self.conn_shared_info.set(from_dev_id, (address[0], address[1], last_catalog_time))
                        else:
                            self.conn_shared_info.set(from_dev_id, _last_info)
                    except Exception as e:
                        print_to_logger(traceback.format_exc())
                        pass
                    print_to_logger('last_catalog_time',last_catalog_time, from_dev_id)

                # # 如果是请求
                if is_request and from_dev_id in gb_gateways:
                    # 消息类型是注册
                    if _type == 'REGISTER':
                        print_to_logger("REGISTER", req_data)
                        # 回复200
                        resp_data = self.common_resp(from_dev_id,headers)
                        self.send_sip_content(from_dev_id, resp_data)
                        print_to_logger("注册包回应成功", headers, resp_data)
                        # 查询网关型号、厂商等信息
                        gw_info_msg = self.gen_gw_info_msg(from_dev_id)
                        self.send_sip_content(from_dev_id, gw_info_msg)
                        print_to_logger("查询网关DeviceInfo", from_dev_id)
                        gevent.sleep(1)
                        # 查询设备目录
                        catlog_msg = self.gen_catalog_msg(from_dev_id)
                        self.send_sip_content(from_dev_id, catlog_msg)
                        print_to_logger("查询网关Catalog", from_dev_id)
                        self.conn_shared_info.set(from_dev_id, (address[0], address[1], time.time()))
                        try:
                            msg_handle_queue.put(json.dumps({"type": "device_catalog_query", "data": {
                                "gb_code": from_dev_id,
                                "time": time.time()
                            }}))
                        except Exception as e:
                            print_to_logger("put to msg_queue error!", str(e))


                    if _type == 'MESSAGE':
                        # 消息类型是 MESSAGE， 且CSeq是 \d+ MESSAGE格式。
                        if re.match(r'\d+ MESSAGE',headers.get('CSeq','')):
                            if content.find('Keepalive') != -1:
                                # 网关的心跳包
                                resp_data = self.common_resp(from_dev_id,headers)
                                self.send_sip_content(from_dev_id, resp_data)
                                print_to_logger('心跳回应成功', headers, resp_data)
                                try:
                                    msg_handle_queue.put(json.dumps({"type": "device_keepalive", "data": {
                                        "gb_code": from_dev_id,
                                        'time': time.time(),
                                    }}))
                                except Exception as e:
                                    print_to_logger("put to msg_queue error!", str(e))

                                # catalog查询逻辑
                                # 上次查询时间距离此刻超过 CATALOG_CHECK_DURATION的值

                                # self.conn_shared_info.set(from_dev_id, _last_info)
                                if time.time() - last_catalog_time > CATALOG_CHECK_DURATION:
                                    catlog_msg = self.gen_catalog_msg(from_dev_id)
                                    self.send_sip_content(from_dev_id, catlog_msg)
                                    print_to_logger("查询网关Catalog", from_dev_id)
                                    self.conn_shared_info.set(from_dev_id, (address[0], address[1], time.time()))

                                # 发送 网关DeviceInfo查询，获取网关的详细信息
                                gw_info_msg = self.gen_gw_info_msg(from_dev_id)
                                self.send_sip_content(from_dev_id, gw_info_msg)
                                print_to_logger("查询网关DeviceInfo", from_dev_id)



                            elif content.find('Catalog') != -1:
                                # 下级网关发过来的设备列表包
                                # 发送响应
                                self.conn_shared_info.set(from_dev_id, (address[0], address[1], time.time()))
                                resp_data = self.common_resp(from_dev_id, headers)
                                self.send_sip_content(from_dev_id, resp_data)
                                # self.socket.sendto(resp_data.encode('gbk'), address)
                                print_to_logger('设备Catalog信息回应成功')
                                # 解析设备信息
                                for raw_dev in re.findall("<Item>.+?</Item>", content, flags=re.DOTALL):
                                    dev = xmltodict.parse(raw_dev)['Item']
                                    device_id = dev.get('DeviceID')
                                    parent_id = dev.get("ParentID", '')
                                    if device_id and "Name" in dev:
                                        Parental = dev.get("Parental", "1")
                                        dev_name = dev['Name']
                                        if Parental == '0' and (dev.get('IPAddress') or dev.get('Address')) \
                                                and 'Manufacturer' in dev and 'Status' in dev:
                                            # 是摄像头
                                            dev_type = dev['Manufacturer']
                                            ip = dev.get('IPAddress') or dev.get('Address') or ''
                                            port = dev.get('Port',None) or ''
                                            lng = dev.get("Longitude","") or ''
                                            lat = dev.get("Latitude","")  or ''
                                            ptz_type = dev.get('Info',{}).get('PTZType', 0)
                                            model = dev.get("Model",'')
                                            is_online =  str(dev.get("Status","")) == 'ON'
                                            print_to_logger(device_id, dev_name, dev_type, ip, port, ptz_type, is_online)
                                            is_cam = True
                                            try:
                                                msg_handle_queue.put(json.dumps({"type": "device_catalog_dev", "data": {
                                                    "code": device_id,
                                                    'name': dev_name,
                                                    'manufacturer': dev_type,
                                                    'ip': ip,
                                                    'port':port,
                                                    'lng': lng,
                                                    'lat': lat,
                                                    'parent_id': parent_id,
                                                    'ptz_type': ptz_type,
                                                    'is_online': is_online,
                                                    "raw_info": raw_dev,
                                                    'gb_code': from_dev_id,
                                                    'model': model,
                                                    'time': int(time.time())
                                                }}))
                                            except Exception as e:
                                                print_to_logger("put to msg_queue error!", str(e))
                                        elif Parental == '1' and  device_id != from_dev_id:
                                            # 是目录
                                            business_groupid = dev.get("BusinessGroupID", '')
                                            if not parent_id:
                                                if len(device_id) % 2 ==0 and len(device_id) <=10 :
                                                    parent_id = device_id[:-2]
                                            print_to_logger(device_id, dev_name, parent_id, business_groupid)
                                            try:
                                                msg_handle_queue.put_nowait(json.dumps({"type": "device_catalog_dir", "data": {
                                                    "code": device_id,
                                                    "name": dev_name,
                                                    'gb_code': from_dev_id,
                                                    'time': int(time.time()),
                                                    "raw_info": raw_dev,
                                                    "parent_id": parent_id,
                                                    'business_groupid': business_groupid,
                                                }}))
                                            except Exception as e:
                                                print_to_logger("put to msg_queue error!", str(e))



                            elif content.find("DeviceInfo") != -1:
                                # 如果是查询网关信息得出来的表
                                resp_data = self.common_resp(from_dev_id, headers)
                                self.send_sip_content(from_dev_id, resp_data)
                                print_to_logger('设备DeviceInfo信息回应成功')
                                if content:
                                    try:
                                        device_info = re.search(r"<Response>.+?</Response>", content, re.DOTALL).group()
                                        #print(device_info)
                                        device_dict = xmltodict.parse(device_info)
                                        code = device_dict['Response']['DeviceID']
                                        name = device_dict['Response'].get('DeviceName','')
                                        manufacturer = device_dict['Response'].get('Manufacturer', '')
                                        model = device_dict['Response'].get('Model', '')

                                    except Exception as e:
                                        print_to_logger("解析DeviceInfo失败！ %s" % content, str(e))
                                    else:
                                        try:
                                            msg_handle_queue.put_nowait(json.dumps({"type": "device_deviceinfo", "data": {
                                                "code": code,
                                                'gb_code': from_dev_id,
                                                "name": name,
                                                'manufacturer': manufacturer,
                                                'model': model
                                            }}))
                                        except Exception as e:
                                            print_to_logger("put to msg_queue error!", str(e))

                            else:
                                print_to_logger("其他消息")
                                resp_data = self.common_resp(from_dev_id, headers)
                                self.send_sip_content(from_dev_id, resp_data)
                                #self.socket.sendto(resp_data.encode('gbk'), address)


                    if _type == 'NOTIFY':
                        # 网关上报过来的NOTIFY信息。（当订阅网关Catalog信息后，网关会上报目录的变动信息。如：设备上下线）
                        # 本部分只对设备上下线消息进行处理
                        #print(_type, headers, content)
                        rsp = self.common_resp(from_dev_id, headers)
                        self.send_sip_content(from_dev_id, rsp)
                        print_to_logger("NOTIFY消息")
                        for dev in re.findall("<Item>.+?</Item>", content, flags=re.DOTALL):
                            dev = xmltodict.parse(dev)['Item']
                            device_id = dev.get('DeviceID', '')
                            event = dev.get("Event", '')
                            if event == 'ON':
                                try:
                                    msg_handle_queue.put_nowait(json.dumps({"type": "device_online_status", "data": {
                                        "code": device_id,
                                        'gb_code': from_dev_id,
                                        "online": True
                                    }}))
                                except Exception as e:
                                    print_to_logger("put to msg_queue error!", str(e))
                            elif event in ('OFF', 'DEFECT', 'DEL'):
                                try:
                                    msg_handle_queue.put_nowait(json.dumps({"type": "device_online_status", "data": {
                                        "code": device_id,
                                        'gb_code': from_dev_id,
                                        "online": False
                                    }}))
                                except Exception as e:
                                    print_to_logger("put to msg_queue error!", str(e))

                # # 如果是回应
                else:
                    if headers.get('CSeq', '') == '2 INVITE':
                        # CSeq 是20 INVITE。  其是和视频流订阅相关的相应
                        print_to_logger("Invite response", _type, headers, content)
                        if _type.startswith('200'):
                            print_to_logger(content)
                            # 目标摄像头通道id
                            channel_id = re.match(r"<sip:([^@]+)@",headers['To']).groups()[0] #re.search("o=(\d+) ", content).groups()[0]
                            print_to_logger("channel_id", channel_id, time.time(), _type)
                            _data = self.invite_ack_success_msg(
                                            from_dev_id,req_headers=headers,
                                                                )
                            self.send_content_to(_data, address)
                            print_to_logger('视频流推流反馈成功', channel_id, _data)
                            try:
                                print_to_logger("to", headers.get('To',''))
                                play_tag_id = re.findall(r";tag=([^;]+)",headers.get('To',''))[-1]
                                print_to_logger("play tag _id ", play_tag_id)
                                redis_conn = redis.Redis.from_url(redis_url)
                                redis_conn.set("callid_tag_%s" % headers['Call-ID'],
                                               json.dumps({"tag_id": play_tag_id,
                                                'Record-Route': headers.get("Record-Route",None)}),86400*7)
                                redis_conn.close()
                            except:
                                pass

                        elif _type.startswith('404') or _type.startswith('400'):
                            print_to_logger("视频流Invite 404", headers, content)
                            self.send_content_to(self.invite_ack_failed_msg(from_dev_id,req_headers=headers), address)


                        elif _type.startswith("603"):
                            print_to_logger("视频流Invite 603", headers, content)
                            self.send_content_to(self.invite_ack_failed_msg(from_dev_id, req_headers=headers), address)

                        elif _type.startswith("500"):
                            print_to_logger("视频流500")
                            #rsp = self.common_response(headers, _type).encode("gbk")
                            #print("999", rsp)
                            #self.socket.sendto(rsp, address)
                            self.send_content_to(self.invite_ack_failed_msg(from_dev_id,req_headers=headers), address)

                        elif _type.startswith("487"):
                            print_to_logger("视频流487", _type)
                            #rsp = self.common_response(headers, _type).encode("gbk")
                            #print("999", rsp)
                            #self.socket.sendto(rsp, address)
                            self.send_content_to(self.invite_ack_failed_msg(from_dev_id,req_headers=headers), address)

                        else:
                            print_to_logger("视频流",_type, re.match(r"<sip:([^@]+)@",headers['To']).groups()[0] )

                    # 如果是PTZ控制相关的回应
                    if headers.get("Call-ID",'').startswith("PTZ_") and 'stop' not in headers.get("Call-ID",''):
                        gevent.sleep(0.3)
                        _call_id = headers.get("Call-ID", '')
                        print_to_logger("try stop ptz")
                        gateway_id = gb_devs[from_dev_id]['code']
                        for _i in range(5):
                            stop_msg = self.gen_ptz_control_msg(gateway_id,
                                                                re.search("<sip:(\d+)@", headers['To']).groups()[0],
                                                                'stop')
                            #print("try stop ptz", stop_msg)
                            gevent.sleep(0.08)
                            self.send_content_to(stop_msg, address)

        except Exception as e:
            print_to_logger("SIP handle error!", str(e))
            print_to_logger(traceback.format_exc())
            pass


def http_handle(sock, addr):
    print_to_logger(sock, time.time())
    request_info = b''
    try:
        with gevent.Timeout(2):
            while 1:
                request_info += sock.recv(1024*1024)
                if b'\r\n\r\n' in request_info:
                    _ = re.search(br"[cC]ontent-[lL]ength: (\d+)", request_info)
                    #print("_", _)
                    if _ :
                        length = int(_.groups()[0])
                        content = request_info.split(b'\r\n\r\n')[1]
                        if len(content) >= length:
                            break
                    else:
                        break
    except (Exception, BaseException) as e :
        print_to_logger("connection read header failed!!", sock, str(e), request_info)
    # print(sock, time.time(),"request_info", request_info)
    try:
        request = request_utils.Request(request_info)
    except Exception as e:
        print_to_logger("error! parse http request failed !", str(e))
    else:
        print_to_logger(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {request.path}")
        if request.path == '/api/invite_camera_from_dev':
            fun = invite_camera_from_dev
        elif request.path == '/api/cancel_invite_camera_from_dev' :
            fun = cancel_invite_camera_from_dev
        elif request.path == '/api/invite_camera':
            fun = invite_camera
        elif request.path == '/api/cancel_invite_camera':
            fun = cancel_invite_camera
        elif request.path == '/api/ptz_control':
            fun = ptz_control
        elif request.path == '/api/gb_devs':
            fun = get_gb_devs
        else:
            content = b'404 Not Found!!!'
            sock.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Length:%s\r\n\r\n%s" % (
                str(len(content)).encode('utf-8'), content))
            sock.close()
            return
        try:
            result = fun(request)
        except Exception as e:
            #traceback.print_exc()
            content = b'500 Internal Server Error!!!' + str(e).encode('utf-8') + traceback.format_exc().encode('utf-8')
            sock.sendall(b"HTTP/1.1 500 Internal Server Error\r\nContent-Length:%s\r\n\r\n%s" %
                         (str(len(content)).encode('utf-8'), content))
            sock.close()
            return
        else:
            content = json.dumps(result).encode('utf-8')
            sock.sendall(b"HTTP/1.1 200 OK\r\nContent-Length:%s\r\n\r\n%s" %
                         (str(len(content)).encode('utf-8'), content))
            sock.close()
            return


forward_processes = []
invite_dev_ip_config = {}
for _i,_j in config.FORWARDER_CONFIG.items():
    for port in _j['PORTS']:
        forward_processes.append((_j['FORWARDER_SERVER_IP'],
                                  port))
    invite_dev_ip_config[_j['FORWARDER_SERVER_IP']] = _j['FORWARDER_RECV_RTP_IP']


#@app.route('/api/invite_camera_from_dev', methods=['GET', 'POST'])
def invite_camera_from_dev(request):
    # 从设备取流
    #print("request,form", request.form)
    global  invite_dev_ip_config
    cam_url = request.form.get('cam_url', '').strip()
    assert cam_url.startswith("gb28181")
    url_obj = parse.urlparse(cam_url)
    gateway_id = url_obj.netloc.strip("/")
    dev_id = url_obj.path.strip("/")
    if gateway_id not in gb_gateways:
        return ({"status": False, "message":"failed! gateway_id %s 不存在！" %  gateway_id,
                             "data":None})
    if "mode" not in request.form:
        mode = gb_gateways[gateway_id]['mode']
    else:
        mode = request.form['mode']
    if 'play_ip' not in request.form:
        my_ip = request.form.get('my_ip', '')
        play_ip = invite_dev_ip_config[my_ip]
    else:
        play_ip = request.form['play_ip']
    play_port = request.form.get('play_port', '')
    play_port = int(play_port)
    msg = sip_server.gen_invite_msg(gateway_id, dev_id, play_ip, play_port, mode.upper())
    print_to_logger("invite_msg", msg)
    try:
        sip_server.send_sip_content(gateway_id, msg)
    except Exception as e:
        print_to_logger("invite camera error!", str(e))
    res = {'status': True, 'message': 'success', 'data': "success"}
    return (res)


#@app.route('/api/cancel_invite_camera_from_dev', methods=['GET', 'POST'])
def cancel_invite_camera_from_dev(request):
    # 取消从设备取流
    #print("request.form", request.form)
    global invite_dev_ip_config
    cam_url = request.form.get('cam_url', '')
    assert cam_url.startswith("gb28181")
    # gb_gateway_addr, device_id = cam_url[10:].split("/")
    url_obj = parse.urlparse(cam_url)
    gateway_id = url_obj.netloc.strip("/")
    dev_id = url_obj.path.strip("/")
    if gateway_id not in gb_gateways:
        return ({"status": False, "message":"failed! gateway_id %s 不存在！" %  gateway_id,
                             "data":None})
    mode = gb_gateways[gateway_id]['mode']
    # play_ip = config.FORWARDER_RECV_RTP_IP
    if 'play_ip' not in request.form:
        my_ip = request.form.get('my_ip', '')
        play_ip = invite_dev_ip_config[my_ip]
    else:
        play_ip = request.form['play_ip']
    play_port = request.form.get('play_port', '')
    play_port = int(play_port)
    msg = sip_server.gen_cancel_invite_msg(gateway_id, dev_id, play_ip, play_port, mode.upper())
    print_to_logger("cancel invite_msg", msg)
    try:
        sip_server.send_sip_content(gateway_id, msg)
    except Exception as e:
        print_to_logger("invite camera error!", str(e))
    res = {'status': True, 'message': 'success', 'data': "success"}
    return (res)



#@app.route('/api/invite_camera', methods=['GET', 'POST'])
def invite_camera(request):
    # 取流， 只允许TCP形式取流
    # print(request.form.items())
    global  forward_processes
    cam_url = request.form.get('cam_url', '')
    assert cam_url.startswith("gb28181")
    #gb_gateway_addr, device_id = cam_url[10:].split("/")
    play_ip = request.form.get('play_ip', '')
    play_port = request.form.get('play_port', '')
    play_port = int(play_port)
    url_obj = parse.urlparse(cam_url)
    _api_ip, _api_port = forward_processes[md5_int(cam_url) % len(forward_processes)]
    #print('invite_camera', cam_url, _api_port)
    res = requests.post("http://{}:{}/api/add_stream_forward".format(_api_ip,
                                                                     _api_port),
                         data={"cam_url": cam_url, "to_ip": play_ip,'to_port': play_port},
                         timeout=3)
    res.close()
    return (res.json())


#@app.route('/api/cancel_invite_camera', methods=['GET', 'POST'])
def cancel_invite_camera(request):
    # 取消取流
    global forward_processes
    cam_url = request.form.get('cam_url', '')
    assert cam_url.startswith("gb28181")
    # gb_gateway_addr, device_id = cam_url[10:].split("/")
    play_ip = request.form.get('play_ip', '')
    play_port = request.form.get('play_port', '')
    play_port = int(play_port)
    url_obj = parse.urlparse(cam_url)
    gateway_id = url_obj.netloc
    dev_id = url_obj.path
    _api_ip, _api_port = forward_processes[md5_int(cam_url) % len(forward_processes)]
    res = requests.post("http://{}:{}/api/remove_stream_forward".format(_api_ip,_api_port),
                        data={"cam_url": cam_url, "to_ip": play_ip, 'to_port': play_port},
                        timeout=3)
    res.close()
    return (res.json())


#@app.route('/api/ptz_control', methods=['GET', 'POST'])
def ptz_control(request):
    # 云台控制
    cam_url = request.form.get('cam_url', '')
    assert cam_url.startswith("gb28181")
    action = request.form.get("action", '')
    assert action in ("left", "right", 'up', 'down',
                      'leftup', 'leftdown', "rightup", "rightdown",
                      'big', 'small',
                      'stop')
    speed = request.form.get("speed", '') or '30'
    zoom_speed = request.form.get('zoom_speed', '') or '3'
    speed = int(speed)
    zoom_speed = int(zoom_speed)
    url_obj = parse.urlparse(cam_url)
    gateway_id = url_obj.netloc
    dev_id = url_obj.path.strip("/")
    # print("invite", nvr_info, device_id, play_ip, play_port)
    msg = sip_server.gen_ptz_control_msg(gateway_id, dev_id, action=action, move_speed=speed, zoom_speed=zoom_speed)
    print_to_logger("ptz control msg", msg, cam_url, gateway_id, dev_id)
    sip_server.send_sip_content(gateway_id, msg)
    res = {'status': True, 'message': 'success', 'data': "success"}
    #redis_conn.close()
    return (res)


def get_gb_devs(request):
    return gb_devs

if __name__ == '__main__':
    # 启动信令服务
    argv = sys.argv
    my_pid = os.getpid()
    sip_server = SipServer(':' + str(sip_server_port), sip_id=my_sip_id, sip_ip=sip_server_ip,
                           sip_port=sip_server_port, contact_route=sip_server_contact_router,
                           spawn=GeventPool(5000))
    sip_server.start()
    http_server = StreamServer(f':{sip_api_port}', handle=http_handle, spawn=GeventPool(3000))
    http_server.start()
    daemon.redirect_output(os.path.join(config.WORK_DIR, "deamon.out"))
    # 多进程模式
    def multi_process_mode(num=4):

        # import daemon
        # daemon.daemon_start()
        process_num = num
        for i in range(1, process_num):
            if os.getpid() == my_pid:
                os.fork()
    multi_process_mode(4)
    #if os.getpid() ==  my_pid:
    print_to_logger("server start success...", os.getpid())
    # multi_process_mode(4)

    # 启动消息处理线程及读数据库线程
    p = gevent.spawn(msg_handle_function)  # 改由协程方式解决
    p1 = gevent.spawn(database_read_thread)     # 改由协程方式解决
    if argv[-1] == 'daemon':
        daemon.daemon_start()
    # daemon.daemon_start()
    print('sip_server start ..', time.time())
    while 1:
        gevent.sleep(0.05)
        sys.stdout.flush()