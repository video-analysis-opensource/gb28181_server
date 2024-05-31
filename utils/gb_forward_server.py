# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/5/27
# 国标流媒体转发服务
import datetime
from gevent.monkey import patch_all;patch_all()
import requests
import gevent,traceback
from gevent.server import DatagramServer,StreamServer
from gevent import pool
import re,random,os,sys,string,time,gzip,datetime,redis
import json, collections, pickle, itertools
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_PATH)
sys.path.append(os.path.join(os.path.dirname(BASE_PATH)))
import config
try:
    import xmltodict,orm_tool, color_print, get_logger, daemon, request_utils
except:
    from . import xmltodict,orm_tool, color_print, get_logger, daemon, request_utils
import hashlib,copy, io
import setproctitle
#from flask import Flask, request, render_template, Response
import bitstring
from urllib import parse
import time
import socket
import multiprocessing
from gevent.queue import Queue
from gevent.socket import create_connection
import functools
import struct
import psutil


def md5_int(_str: str):
    _ = hashlib.md5(_str.encode('utf-8')).hexdigest()
    return int(_, 16)


os.system("mkdir -p %s" % config.WORK_DIR)
sip_work_dir = os.path.join(config.WORK_DIR, "sip_server")
log_dir = os.path.join(config.WORK_DIR, "logs")
os.system("mkdir -p %s" % sip_work_dir)
os.system("mkdir -p %s" % log_dir)
#log_obj = get_logger.get_logger(os.path.join(log_dir,"gb_forward_server.log"), backupCount=10)
green_pool = pool.Pool(1000)
sip_port = config.SIP_SERVER_API_PORT


def print_to_logger(*args):
    file_name = os.path.join(log_dir, f"gb_forward_server-{datetime.datetime.now().strftime('%Y%m%d')}.log")
    now = datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds')
    try:
        msg = " ".join([str(i) for i in args ])
        with open(file_name, "a+") as f:
            f.write(f"[{now}: INFO]:{msg}\n")
    except:
        pass


print_to_logger("开始启动服务...")


def detect_one_port(start_port=12000):
    # 选择一个端口
    for i in range(start_port + random.randrange(0, 5000, 10), 25000, 2):
        try:
            udp_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_s.bind(('0.0.0.0', i))
            udp_s1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_s1.bind(('0.0.0.0', i+1))
            tcp_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_s.bind(('0.0.0.0', i))
            tcp_s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_s1.bind(('0.0.0.0', i + 1))
            udp_s.close()
            udp_s1.close()
            tcp_s.close()
            tcp_s1.close()
        except:
            try:
                udp_s.close()
            except:
                pass
            try:
                udp_s1.close()
            except:
                pass
            try:
                tcp_s.close()
            except:
                pass
            try:
                tcp_s1.close()
            except:
                pass
        else:
            return i


def invite_from_dev(cam_url, play_port):
    try:
        resp = requests.post("http://{}:{}/api/invite_camera_from_dev".format(config.SIP_SERVER_IP,
                                                                              sip_port),
                             data={'cam_url': cam_url,
                                   'play_port': play_port,
                                   'my_ip': MY_IP},
                             timeout=3)
        print_to_logger(resp.content,resp.headers)
        print_to_logger("force invite from dev success ", cam_url,  play_port, resp.json())
    except Exception as e:
        print_to_logger("force invite from dev failed", cam_url,  play_port, str(e))


def cancel_invite_from_dev(cam_url, play_port):
    try:
        resp = requests.post("http://{}:{}/api/cancel_invite_camera_from_dev".format(config.SIP_SERVER_IP,
                                                                              sip_port),
                             data={'cam_url': cam_url,
                                   'play_port': play_port,
                                   'my_ip': MY_IP},
                             timeout=3)
        print_to_logger(resp.content,resp.headers)
        print_to_logger("force_cancel_invite success", cam_url, play_port, resp.json())
    except Exception as e:
        print_to_logger("force_cancel_invite failed", cam_url, play_port, str(e))


class RtcpClient(DatagramServer):

    def __init__(self, *args, client, **kwargs):
        DatagramServer.__init__(self, *args, **kwargs)
        self.client = client

    def handle(self, data: bytes, addr):
        data_array = bitstring.BitArray(data)
        print_to_logger("rtcp_data", data_array)
        _type = data_array[8:16].uint
        if _type == 200:
            resp = self.get_recv_report(data, self.client.cycle_num, self.client.seq_num)
            print_to_logger("rtcp_resp_data", bitstring.BitArray(resp))
            self.socket.sendto(resp, addr)

    def get_recv_report(self, sr_info: bytes, sq_cycle_count: int, sq_num: int):
        bit_str = bitstring.BitArray(sr_info)
        sender_ccrc = bit_str[32:64]
        _time = bit_str[80:112]
        recv_report = bitstring.BitArray(hex="0x81c90006") + \
                      bitstring.BitArray(uint=sender_ccrc.uint - 1, length=32) + \
                      sender_ccrc + bitstring.BitArray(hex="0x00000000") + \
                      bitstring.BitArray(uint=sq_cycle_count, length=16) + bitstring.BitArray(uint=sq_num,
                                                                                              length=16) \
                      + bitstring.BitArray(hex='0x0000001a') + _time + \
                      bitstring.BitArray(hex="0x00000299")

        ss_desc = bitstring.BitArray(hex="81ca0007") + bitstring.BitArray(uint=sender_ccrc.uint - 1,
                                                                          length=32) + \
                  bitstring.BitArray(hex="0x0110") + bitstring.BitArray(
            b"gb28181_py------") + bitstring.BitArray(hex="0x0000")
        return (recv_report + ss_desc).bytes

class RTPClient(DatagramServer):

    def __init__(self, *args, res_queues, **kwargs):
        DatagramServer.__init__(self, *args, **kwargs)
        self.last_data_time = time.time()
        self.seq_num = 0
        self.cycle_num = 0
        self.rtp_buff = {}
        self.rtp_cursor = None
        self.rtp_counter = 0
        self._buff = b''
        self._buff_send_time = time.time()
        self.res_queues = res_queues


    @staticmethod
    def cmp(a, b):
        seq_a = a[0]
        seq_b = b[0]
        if seq_a - seq_b > 10000:
            return -1
        else:
            if seq_a < seq_b:
                return -1
            elif seq_a == seq_b:
                return 0
            elif seq_a > seq_b:
                return 1

    def handle(self, data, address):
        print_to_logger("udp received", address,len(data))
        #bit_data = bitstring.BitArray(data[:12])
        self.last_data_time = time.time()
        try:
            seq_num = struct.unpack(">H", data[2:4])[0]
            #seq_num = bitstring.BitArray(data[2:4]).uint
        except Exception as e:
            print_to_logger(str(e))
        else:
            # print(seq_num)
            if self.seq_num:
                if seq_num - self.seq_num != 1:
                    print_to_logger("包乱序###############", seq_num, self.seq_num)
            if seq_num == 65535:
                self.cycle_num += 1
            self.seq_num = seq_num
            self.rtp_counter += 1
            # 初始化rtp_cursor
            if self.rtp_cursor == None:
                self.rtp_cursor = max(seq_num -1, 0)
                print_to_logger("初始化rtp_cursor", self.rtp_cursor)
            # data放入 rtp_buff
            self.rtp_buff[seq_num] = data
            # 如果已经收到20个包
            if self.rtp_counter >= 20:
                # 通过rtp_cursor 尝试取数据
                j = self.rtp_cursor + 1
                # 遍历次数计数器
                while_count = 0
                while True:
                #for i in range(self.rtp_cursor+1, self.rtp_cursor + 65535):
                    _ = j % 65536
                    j += 1
                    while_count += 1
                    if while_count > 5000:
                        break
                    try:
                        _info = self.rtp_buff.pop(_)
                        self.rtp_cursor = _
                    except:
                        pass
                    else:
                        self._buff += (struct.pack('>H', len(_info)) +
                                                  _info)
                        break
            now_time = time.time()
            if now_time - self._buff_send_time > 0.1:
                # 成功取到数据
                for q in self.res_queues:
                    try:
                        q.put_nowait(self._buff)
                    except Exception as e:
                        print_to_logger("RTP rts_queue put failed", str(e))
                self._buff = b''
                self._buff_send_time = now_time



class TCPRTPClient(object):
    def __init__(self, *args, res_queues, **kwargs):
        self.res_queues = res_queues
        self.last_data_time = time.time()
        self.closed = False
        self._buff = b''
        self._buff_len = 0
        self._buff_send_time = time.time()
        def tcp_handle(sock, addr):
            print_to_logger("tcp rtp client  connected!!!", sock, addr)
            while 1:
                if sock.closed or self.closed:
                    # 如果socket被关闭 或者 超过8秒未获取到数据
                    print_to_logger("end.....")
                    print_to_logger("stop.....")
                    return
                try:
                    with gevent.Timeout(2):
                        data = sock.recv(1024*1024*2)
                        data_len = len(data)
                except ConnectionResetError as e:
                    break
                except (Exception, BaseException, gevent.Timeout) as e:
                    print_to_logger("recv exception", str(e))
                    gevent.sleep(0.01)
                    continue
                if not data:
                    gevent.sleep(0.01)
                    continue
                else:
                    now_time = time.time()
                    self.last_data_time = now_time
                    self._buff += data
                    self._buff_len += data_len
                    if now_time - self._buff_send_time >= 0.1:
                        content = b''
                        while 1:
                            if self._buff[:2] != b'':
                                _len = bitstring.BitArray(self._buff[:2]).uint
                                if self._buff_len >= _len + 2:
                                    content += self._buff[:2+_len]
                                    self._buff = self._buff[(2+_len):]
                                    self._buff_len = self._buff_len - (2+_len)
                                else:
                                    break
                            else:
                                break
                        if content:
                            for q in self.res_queues:
                                try:
                                    q.put_nowait(content)
                                except Exception as e:
                                    print_to_logger("TCPRTP rts_queue put failed", str(e))
                            self._buff_send_time = now_time

        self.stream_server = StreamServer(*args, handle=tcp_handle, **kwargs)

    def stop(self):
        self.closed = True
        try:
            self.stream_server.close()
        except:
            pass
        try:
            self.stream_server.stop()
        except:
            pass

    def start(self):
        self.closed = False
        self.stream_server.start()

    def socket(self):
        return self.stream_server.socket


class MyQueue(object):
    # 轻量化的队列的实现
    def __init__(self, name, maxsize):
        self.name = name
        self._max_size = maxsize
        self.size = 0
        self._q = []

    def put_nowait(self,item):
        if self.size < self._max_size:
            self._q.append(item)
            self.size += 1
        else:
            raise Exception("Queue Full!")


    def get_nowait(self):
        try:
            item = self._q.pop(0)
            self.size -= 1
            return item
        except:
            return None


class SupremeForwarder(object):
    # RTP流转发类抽象
    TIMEOUT = 10
    def __init__(self, port, gateway_id, dev_id , **kwargs):
        print_to_logger("port", port)
        self.port = port
        self.gateway_id = gateway_id
        self.device_id = dev_id
        self.queues = []
        # udp模式接收
        self.rtp_client = RTPClient(":%s" % (int(port)), res_queues=self.queues)
        self.rtcp_client = RtcpClient(":%s" % (int(port) + 1), client=self.rtp_client)
        # tcp模式接收
        self.rtptcp_client = TCPRTPClient(":%s" % (int(port)), res_queues=self.queues)
        # 启动接收服务
        self.rtp_client.start()
        self.rtcp_client.start()
        self.rtptcp_client.start()
        recv_buff = self.rtp_client.socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
        print_to_logger("rtp_client recv buff", recv_buff)
        self.rtp_client.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024 * 1024 * 5)
        # invite流
        invite_from_dev(self.cam_url, self.port)
        self.stopped = False
        # 启动转发协程
        self.start_time = time.time()
        self.to_conns = []



    def add_ip_port(self, ip, port):
        port = int(port)
        def forward_fun(queue, ip=ip, port=port, timeout=self.TIMEOUT):
            # 尝试连接
            for i in range(10):
                try:
                    to_conn = create_connection((ip, int(port)), 2)
                    break
                except :
                    gevent.sleep(0.05)
                    print_to_logger("forward", self.cam_url, "try connect", ip, port, i, " failed")
                    pass
            else:
                print_to_logger("forward", self.cam_url, "connect", ip, port, "failed !!!")
                # 连接失败。
                try:
                    print_to_logger("del queue", self.cam_url, ip, port)
                    self.queues.remove(queue)
                except:
                    pass
                return
                # self.stop_serv()
                # force_cancel_invite(self.cam_url, ip, port)
            to_conn.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024)
            self.to_conns.append(to_conn)
            while 1:
                # 如果超过TIMEOUT还未收到新数据，就认为断开了。
                if queue not in self.queues or time.time() - self.last_data_time > timeout or self.stopped:
                    try:
                        self.queues.remove(queue)
                    except:
                        pass
                    # 关闭连接
                    try:
                        to_conn.close()
                    except:
                        pass
                    return
                try:
                    bytes_data = queue.get_nowait()
                    assert bytes_data
                except Exception as e:
                    gevent.sleep(0.05)
                else:
                    try:
                        to_conn.sendall(bytes_data)
                    except Exception as e:
                        print_to_logger("forward {}  send data error {}".format(self.cam_url, str(e)))
                        try:
                            to_conn.close()
                        except:
                            pass
                        try:
                            print_to_logger("del queue", self.cam_url, ip, port)
                            self.queues.remove(queue)
                        except:
                            pass
                        return

        queue = MyQueue(name=f"{ip}-{port}", maxsize=500)
        green_pool.spawn(forward_fun, queue, ip, port)
        self.queues.append(queue)

    @property
    def cam_url(self):
        return "gb28181://{}/{}".format(self.gateway_id, self.device_id)

    @property
    def last_data_time(self):
        # 获取上一个包的时间
        return max(self.rtp_client.last_data_time, self.rtptcp_client.last_data_time)

    def stop_serv(self):
        try:
            cancel_invite_from_dev(self.cam_url, self.port)
        except Exception as e:
            print_to_logger("cancel_invite_from_dev error!", self.cam_url, str(e))
        try:
            self.rtcp_client.stop()
        except:
            pass
        try:
            self.rtp_client.stop()
        except:
            pass
        try:
            self.rtptcp_client.stop()
        except:
            pass
        self.queues = []
        self.stopped = True
        for conn in self.to_conns:
            try:
                conn.close()
            except:
                pass
        self.to_conns = []


# 轻量的http server的实现
def http_handle(sock, addr):
    request_info = b''
    try:
        with gevent.Timeout(2):
            while 1:
                request_info += sock.recv(1024 * 1024)
                if b'\r\n\r\n' in request_info:
                    _ = re.search(br"[cC]ontent-[lL]ength: (\d+)", request_info)
                    # print("_", _)
                    if _:
                        length = int(_.groups()[0])
                        # print("length", length, len(request_info.split(b'\n\n\r\n')[1]),
                        # request_info.split(b'\r\n\r\n')[1])
                        if len(request_info.split(b'\r\n\r\n')[1]) >= length:
                            break
    except (Exception, BaseException) as e:
        print_to_logger("connection read header failed!!", sock, str(e), request_info)
    #print("gb_forward raw_info" , request_info)
    try:
        request = request_utils.Request(request_info)
    except Exception as e:
        print_to_logger("error! parse http request failed !", str(e))
    else:
        print_to_logger(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {request.path}")
        if request.path == '/api/add_stream_forward':
            fun = add_stream_forward
        elif request.path == '/api/remove_stream_forward' :
            fun = remove_stream_forward
        elif request.path  == "/tasks":
            fun = tasks
        else:
            content = b'404 Not Found!!!'
            sock.sendall(b"HTTP/1.1 404 Not Found\r\nContent-Length:%s\r\n\r\n%s" % (
                str(len(content)).encode('utf-8'), content))
            sock.close()
            return

        try:
            result = fun(request)
        except Exception as e:
            traceback.print_exc()
            content = b'500 Internal Server Error!!!' + str(e).encode('utf-8')
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



def add_stream_forward(request):
    cam_url = request.form.get("cam_url")
    to_ip = request.form.get("to_ip")
    to_port = request.form.get("to_port")
    url_obj = parse.urlparse(cam_url)
    gateway_id = url_obj.netloc.strip("/")
    dev_id = url_obj.path.strip("/")
    if  cam_url  not  in all_forwarder:
        all_forwarder[cam_url] = SupremeForwarder(detect_one_port(), gateway_id=gateway_id,
                                                                    dev_id=dev_id)
    all_forwarder[cam_url].add_ip_port(to_ip, int(to_port))
    return ({"status": True, "data": True,
                         "message": "success"})


def remove_stream_forward(request):
    cam_url = request.form.get("cam_url")
    to_ip = request.form.get("to_ip")
    to_port = request.form.get("to_port")
    url_obj = parse.urlparse(cam_url)
    gateway_id = url_obj.netloc
    dev_id = url_obj.path
    if cam_url in all_forwarder:
        target_queue = None
        for q in all_forwarder[cam_url].queues:
            if q.name == f"{to_ip}-{to_port}":
                target_queue = q
        try:
            all_forwarder[cam_url].queues.remove(target_queue)
        except Exception as e:
            #print(str(e))
            pass
    return ({"status": True, "data": True,
                         "message": "success"})


def tasks(request):
    data = []
    for i,j in all_forwarder.items():
        data.append(i, len(j.queues))
    return ({"status": True, "data": data,
             "message": "success"})


if __name__ == '__main__':
    # 多进程模式执行
    argv = sys.argv
    setproctitle.setproctitle("gbs_forward_server")
    my_pid = os.getpid()
    all_forwarder = {}
    ifconfig_addrs = [i[0].address  for i in   psutil.net_if_addrs().values()]
    my_config = None
    MY_IP = ''
    for i,j in config.FORWARDER_CONFIG.items():
        if j['FORWARDER_SERVER_IP'] in ifconfig_addrs:
            MY_IP = j['FORWARDER_SERVER_IP']
            my_config = j
            break
    if not my_config:
        print("FORWARDER_CONFIG 中无当前主机的配置！请检查后重试！")
        sys.exit(-1)

    _len = len(my_config['PORTS'])
    assert _len >= 1
    bind_port = None
    daemon.redirect_output(os.path.join(config.WORK_DIR,"deamon.out"))
    for _i, port in enumerate(my_config['PORTS']):
        if _i == 0:
            # 第一个不用fork
            bind_port = port
            # break
        else:
            # 从第二个开始每个fork一下
            os.fork()
            if os.getpid() != my_pid:
                bind_port = port
                break
    print_to_logger(os.getpid(), bind_port)
    print_to_logger("start success on ", bind_port)
    http_server = StreamServer((':%s' % int(bind_port)), handle=http_handle)
    http_server.start()
    if argv[-1] == 'daemon':
        daemon.daemon_start()
    print('forward_server start ..', time.time())
    while 1:
        gevent.sleep(4)
        for key in list(all_forwarder.keys()):
            if all_forwarder[key].queues == []:
                all_forwarder[key].stop_serv()
            if all_forwarder[key].stopped:
                del all_forwarder[key]

