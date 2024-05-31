# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/1/17
# httpflv流媒体转发核心逻辑
from gevent.monkey import patch_all;patch_all(thread=False,subprocess=False)
from multiprocessing import Queue
import gevent
import multiprocessing
import av
import time
import io
import traceback
import psutil
from urllib import parse
import socket
import random
import sys, os
import urllib.parse
import setproctitle
import hashlib, base64, struct, time
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_PATH)
sys.path.append(os.path.join(os.path.dirname(BASE_PATH)))
import config
from gevent.queue import Queue as GQueue
try:
    import xmltodict,orm_tool, color_print, get_logger, daemon
except:
    from . import xmltodict,orm_tool, color_print, get_logger, daemon


os.system("mkdir -p %s" % config.WORK_DIR)
log_dir = os.path.join(config.WORK_DIR, "logs")
os.system("mkdir -p %s" % log_dir)
log_obj = get_logger.get_logger(os.path.join(log_dir,"gb_httpflv_server.log"), backupCount=10)


def print_to_logger(*args):
    try:
        log_obj.info(" ".join([str(i) for i in args ]))
    except:
        pass

print_to_logger("开始启动服务...")

def detect_one_port(start_port=25000, mode='TCP'):
    assert mode in ("TCP", 'UDP')
    #gevent.sleep(random.random() / 3)
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


def av_function(cam_url, queue, port):
    import time
    print_to_logger("start av_ function", time.time() , cam_url)
    print_to_logger(servers)
    for s in servers:
        s.stop_accepting()
    import setproctitle
    setproctitle.setproctitle("gbs_httpflv %s" % cam_url)
    from gevent.monkey import patch_all;patch_all(thread=False,subprocess=False)
    gevent.reinit()
    from gevent.server import DatagramServer, StreamServer
    import bitstring
    import functools
    import copy
    import time
    import sys
    sys.path.append(os.path.abspath(os.path.dirname(__file__)))
    try:
        import ps_parser
    except:
        from . import ps_parser

    class FileObj(object):
        def __init__(self, name, queue=queue):
            self.name = name
            self.queue=queue
            # self.file = open(name,"wb")

        def write(self, info: bytes):
            pass
            # try:
            #     #self.file.write(info)
            #     self.queue.put_nowait(info)
            # except Exception as e:
            #     print_to_logger("put failed")
            #     print_to_logger(traceback.format_exc())
            #     sys.exit()

    # tcp 模式
    def tcp_handle(sock, addr):
        stream_type = None
        codec = None
        file_obj = FileObj("123.flv")
        _output = av.open(file_obj, 'w')
        _out_stream = None
        print_to_logger(sock, time.time())
        def packet_handle(h26x_frame_bytes: bytes, _time:int=None):
            "包处理函数"
            if codec:
                try:
                    packets = codec.parse(h26x_frame_bytes)
                    #print(len(packets), packets, _time)
                    for packet in packets:
                        #print(packet, _time)
                        packet.stream = _out_stream
                        #print(packet.time_base)
                        packet.time_base = '1/90000'
                        packet.dts = _time
                        packet.pts = _time
                        print_to_logger(cam_url, packet)
                        #packet.pts = self._last_pts[0] if len(self._last_pts) >= 15 else 0
                        #self._last_pts.append(_time)
                        #self._last_pts = self._last_pts[-15:]
                        # if '264' in codec.name:
                        #     # 对于x264编码的packet 直接mux进去
                        #     try:
                        #         _output.mux(packet)
                        #     except (Exception, BaseException) as e:
                        #         print("h264 mux except:", str(e))
                        # else:
                        frames = codec.decode(packet)
                        #err = av.logging.get_last_error()
                        # if err[0] != 0 and err[0] != self.last_err:
                        #     print(packet, err)
                        #     self.last_err = err[0]
                        #     continue
                        if len(frames):
                            # print(packet,_time, self._last_pts)
                            # else:
                                # 对x265编码的packet。 先编码再mux
                            for frame in frames:
                                try:
                                    _out_stream.width = 960
                                    _out_stream.height = 540
                                    _packets = _out_stream.encode(frame)
                                    for _p in _packets:
                                        try:
                                            # self.file.write(info)
                                            queue.put_nowait(cam_url.encode("utf-8") + _p.to_bytes())
                                        except Exception as e:
                                            print_to_logger("put failed")
                                            print_to_logger(traceback.format_exc())
                                            sys.exit()
                                        # _output.mux(_p)
                                        #print_to_logger(cam_url, _p)
                                except (Exception, BaseException) as e:
                                    print_to_logger("decode and mux except:", str(e))

                            #self._last_pts = _time
                        break

                except Exception as e:
                    print_to_logger(str(e)), "xxx"

        buff = b''
        last_data_time = time.time()
        rtp_data_list = []
        while 1:
            data = sock.recv(1024*10*5)
            # print(time.time(), len(data))
            #continue
            if sock.closed or time.time() - last_data_time > 8:
                # 如果socket被关闭 或者 超过8秒未获取到数据
                print_to_logger("end.....")
                break
            if not data:
                #gevent.sleep(0.00)
                continue
            else:
                last_data_time = time.time()
            buff += data
            while 1:
                if not buff:
                    break
                _len = bitstring.BitArray(buff[:2]).uint
                if len(buff) >= _len + 2:

                    rtp_frame_data = buff[2:2+_len]
                    buff = buff[2 + _len:]
                    bit_data = bitstring.BitArray(rtp_frame_data)
                    try:
                        pt = bit_data[9:16]
                        cc = bit_data[4:8]
                        is_end = bit_data[8]
                        seq_num = bit_data[16:32].uint
                        timestamp = bit_data[32:64].uint
                        # print(seq_num,len(data), bit_data[:512+64], is_end, timestamp )
                        # print(seq_num, "_____len", _len, is_end)
                    except Exception as e:
                        # print(str(e))
                        pass
                    else:
                        # if pt.uint in (96, 97, 98):
                        rtp_data = bit_data[96:].tobytes()
                        rtp_data_list.append(rtp_data)
                        if is_end:
                            ps_frame_data = b"".join(rtp_data_list)
                            # print(time.time(), bitstring.BitArray(ps_frame_data)[:1024],
                            #       timestamp,"ps_len",len(ps_frame_data))
                            rtp_data_list = []
                            #print("ps_frame_data", ps_frame_data[:50])
                            if ps_frame_data.startswith(b"\x00\x00\x01\xba"):
                                if stream_type == None:
                                    stream_type = ps_parser.get_stream_type_from_ps(ps_frame_data) or 'h264'
                                    print_to_logger("流类型为", stream_type)
                                    codec = av.CodecContext.create(stream_type, "r")
                                    _out_stream = _output.add_stream(codec_name='h264', rate=20)
                                    _out_stream.codec_context.options = {
                                        'tune': 'zerolatency',
                                        'preset': 'ultrafast'
                                    }
                                    print_to_logger("codec", codec, time.time())

                                res = ps_parser.get_raw_stream_from_ps(ps_frame_data, with_pts=True)
                                if res and res[0]:
                                    h26x_data, pts = res
                                    #print(pts,h26x_data[:100],"h26x_len", len(h26x_data))
                                    # print("pts", pts)
                                    packet_handle(h26x_data, pts)
                        else:
                            pass
                else:
                    break
    client = StreamServer(":%s" % port, handle=tcp_handle)
    client.start()
    client.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*10*10)
    print_to_logger("client start", client, queue, time.time())
    while 1:
        gevent.sleep(1)


my_ip = config.HTTPFLV_SERVER_IP
my_recv_stream_ip = config.HTTPFLV_RECV_RTP_IP

cam_url_share_queue = {}
cam_url_queues = {}


class Header(object):
    __slots__ = ('fin', 'mask', 'opcode', 'flags', 'length')

    FIN_MASK = 0x80
    OPCODE_MASK = 0x0f
    MASK_MASK = 0x80
    LENGTH_MASK = 0x7f

    RSV0_MASK = 0x40
    RSV1_MASK = 0x20
    RSV2_MASK = 0x10

    # bitwise mask that will determine the reserved bits for a frame header
    HEADER_FLAG_MASK = RSV0_MASK | RSV1_MASK | RSV2_MASK

    def __init__(self, fin=0, opcode=0, flags=0, length=0):
        self.mask = ''
        self.fin = fin
        self.opcode = opcode
        self.flags = flags
        self.length = length

    def mask_payload(self, payload):
        payload = bytearray(payload)
        mask = bytearray(self.mask)

        for i in range(self.length):
            payload[i] ^= mask[i % 4]

        return payload

    # it's the same operation
    unmask_payload = mask_payload

    def __repr__(self):
        opcodes = {
            0: 'continuation(0)',
            1: 'text(1)',
            2: 'binary(2)',
            8: 'close(8)',
            9: 'ping(9)',
            10: 'pong(10)'
        }
        flags = {
            0x40: 'RSV1 MASK',
            0x20: 'RSV2 MASK',
            0x10: 'RSV3 MASK'
        }

        return ("<Header fin={0} opcode={1} length={2} flags={3} mask={4} at "
                "0x{5:x}>").format(
                    self.fin,
                    opcodes.get(self.opcode, 'reserved({})'.format(self.opcode)),
                    self.length,
                    flags.get(self.flags, 'reserved({})'.format(self.flags)),
                    self.mask, id(self)
        )

    @classmethod
    def decode_header(cls, stream):
        """
        Decode a WebSocket header.

        :param stream: A file like object that can be 'read' from.
        :returns: A `Header` instance.
        """
        read = stream.read
        data = read(2)

        if len(data) != 2:
            raise Exception("Unexpected EOF while decoding header")

        first_byte, second_byte = struct.unpack('!BB', data)

        header = cls(
            fin=first_byte & cls.FIN_MASK == cls.FIN_MASK,
            opcode=first_byte & cls.OPCODE_MASK,
            flags=first_byte & cls.HEADER_FLAG_MASK,
            length=second_byte & cls.LENGTH_MASK)

        has_mask = second_byte & cls.MASK_MASK == cls.MASK_MASK

        if header.opcode > 0x07:
            if not header.fin:
                raise Exception(
                    "Received fragmented control frame: {0!r}".format(data))

            # Control frames MUST have a payload length of 125 bytes or less
            if header.length > 125:
                raise Exception(
                    "Control frame cannot be larger than 125 bytes: "
                    "{0!r}".format(data))

        if header.length == 126:
            # 16 bit length
            data = read(2)

            if len(data) != 2:
                raise Exception('Unexpected EOF while decoding header')

            header.length = struct.unpack('!H', data)[0]
        elif header.length == 127:
            # 64 bit length
            data = read(8)

            if len(data) != 8:
                raise Exception('Unexpected EOF while decoding header')

            header.length = struct.unpack('!Q', data)[0]

        if has_mask:
            mask = read(4)

            if len(mask) != 4:
                raise Exception('Unexpected EOF while decoding header')

            header.mask = mask

        return header

    @classmethod
    def encode_header(cls, fin, opcode, mask, length, flags):
        """
        Encodes a WebSocket header.

        :param fin: Whether this is the final frame for this opcode.
        :param opcode: The opcode of the payload, see `OPCODE_*`
        :param mask: Whether the payload is masked.
        :param length: The length of the frame.
        :param flags: The RSV* flags.
        :return: A bytestring encoded header.
        """
        first_byte = opcode
        second_byte = 0
        extra = b""
        result = bytearray()

        if fin:
            first_byte |= cls.FIN_MASK

        if flags & cls.RSV0_MASK:
            first_byte |= cls.RSV0_MASK

        if flags & cls.RSV1_MASK:
            first_byte |= cls.RSV1_MASK

        if flags & cls.RSV2_MASK:
            first_byte |= cls.RSV2_MASK

        # now deal with length complexities
        if length < 126:
            second_byte += length
        elif length <= 0xffff:
            second_byte += 126
            extra = struct.pack('!H', length)
        elif length <= 0xffffffffffffffff:
            second_byte += 127
            extra = struct.pack('!Q', length)
        else:
            raise Exception("too large frame")

        if mask:
            second_byte |= cls.MASK_MASK

        result.append(first_byte)
        result.append(second_byte)
        result.extend(extra)

        if mask:
            result.extend(mask)

        return result


def handle(sock, address):
    global cam_url_queues, cam_url_share_queue
    import requests
    print_to_logger("connected",os.getpid(), sock, address, time.time())
    request_data_raw = sock.recv(8192)
    print_to_logger(request_data_raw)
    try:
        request_data = request_data_raw.decode("utf-8").splitlines()
        base_info = request_data[0]
        _a,_b,_c = base_info.split()
        if _a == 'GET':
            path = _b
            query_info = path.split("?")[1]
            query_dict = dict(parse.parse_qsl(query_info))
            assert "cam_url" in query_dict and query_dict['cam_url'],\
                Exception('无法找到cam_url参数')
            cam_url = query_dict['cam_url'].strip(".flv")
            _ = [[j.strip() for j in i.split(":", 1)] for i in request_data[1:]]
            headers = dict([i for i in _ if len(i)==2])
            if headers.get("Upgrade") == 'websocket':
                is_websocket = True
                ws_key = headers.get('Sec-WebSocket-Key', '')
            else:
                is_websocket = False
                ws_key = ''
            print_to_logger(headers, is_websocket, ws_key, cam_url)
        else:
            raise Exception("must be GET!")
    except Exception as e:
        print_to_logger(str(e))
        sock.send(b"HTTP/1.1 404 Not Found\r\n\r\nNot Found")
    else:
        if not is_websocket:
            sock.send(b"HTTP/1.1 200 OK\r\n" +
                      b"Access-Control-Allow-Methods: GET, OPTIONS\r\n"+
                      b"Access-Control-Allow-Origin: *\r\n"+
                      b"Access-Control-Allow-Credentials: true\r\n" +
                      b"Content-Type: video/x-flv\r\n"+
                      b"\r\n")
        else:
            msg = b'HTTP/1.1 101 Switching Protocols\r\n' + \
                      b'Upgrade: websocket\r\n'+ \
                      b'Connection: Upgrade\r\n' + \
                      (b'Sec-WebSocket-Accept: %s\r\n\r\n' % base64.b64encode(hashlib.sha1(ws_key.encode() +
                                      b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest()) )
            #print(msg)
            sock.send(msg)
        # print("akakakak")
        print_to_logger("send http header", time.time())
        def invite_camera(cam_url, ip, port):
            try:
                resp = requests.post("http://{}:{}/api/invite_camera".format(config.SIP_SERVER_IP,
                                                                             config.SIP_SERVER_API_PORT),
                                     data={'cam_url': cam_url,
                                           'play_ip': ip,
                                           'play_port': port,
                                           },
                                     timeout=3).json()
                print_to_logger(resp)
                call_id = resp['data']
                assert call_id
                return call_id
            except Exception as e:
                print_to_logger("invite camera error", str(e), cam_url)
                return None

        def cancel_invite_camera(cam_url, ip, port):
            try:
                resp = requests.post("http://{}:{}/api/cancel_invite_camera".format(config.SIP_SERVER_IP,
                                                                                    config.SIP_SERVER_API_PORT),
                                     data={'cam_url': cam_url,
                                           'play_ip': ip,
                                           'play_port': port
                                           },
                                     timeout=3).json()
                print_to_logger('cancel_invite_camera', cam_url, resp)
            except Exception as e:
                print_to_logger("cancel invite camera error", str(e), cam_url)
                return None

        for p in psutil.Process(pid=os.getpid()).children(True):
            try:
                p_name = p.name()
                p_cmdline = [p.cmdline()]
                if 'gbs_httpflv' == p_cmdline[0].strip() and cam_url == p_cmdline[1].strip():
                    # 已经在运行了
                    break
            except:
                pass
        else:
            # 没有在执行，  尝试启动流媒体进程

            # cam_url_share_queue[cam_url] = _q
            port = detect_one_port(mode='TCP')
            process = multiprocessing.Process(target=av_function,args=(cam_url, cam_url_share_queue,
                                                                       port),
                                              daemon=True)
            process.start()
            call_id = invite_camera(cam_url, my_ip, port)
            print_to_logger("5", time.time(), "call_id", call_id)

        last_data_time = time.time()

        def send_data(info:bytes):
            if not is_websocket:
                try:
                    sock.sendall(info)
                except Exception as e:
                    print_to_logger("sock.sendall error", str(e))
                    return False
            else:
                header = Header.encode_header(True, 0x02, b'', len(info), 0)
                try:
                    sock.sendall(header + info)
                except Exception as e:
                    print_to_logger("sock.sendall error", str(e))
                    return False
            return True


        gqueue = GQueue(maxsize=50)
        cam_url_queues.setdefault(cam_url, [])
        cam_url_queues[cam_url].append(gqueue)


        class FileObj(object):
            def __init__(self, name, *args, **kwargs):
                self.name = name

            def write(self, info: bytes):
                res = send_data(info)
                if not res:
                    raise Exception("write failed!!! send_data error!")

        file_obj = FileObj("123.flv")
        _output = av.open(file_obj, 'w')
        _out_stream = _output.add_stream(codec_name='h264', rate=20)
        
        _out_stream.codec_context.options = {
            'tune': 'zerolatency',
            'preset': 'ultrafast'
        }


        while 1:
            # try:
            #     with gevent.Timeout(0.001) as t:
            #         data = sock.recv(1024)
            #         print("recv data", data)
            # except (gevent.Timeout, BaseException) as _e:
            #     pass
            gevent.sleep(0.001)
            # print(dir(sock))
            if sock.closed  or time.time() - last_data_time > 15:
                # 如果socket被关闭 或者 超过15秒未获取到数据
                print_to_logger("end.....")
                break
            if queue.qsize() > 100:
                # 如果队列长度大于100， 扔掉50个元素。导致队列长度超过100的原因一般是网络不畅。
                for i in range(50):
                    try:
                        queue.get_nowait()
                    except:
                        pass
            try:
                info = queue.get_nowait()
                assert len(info) > 0
            except Exception as e:
                pass
            else:
                last_data_time = time.time()
                #print("send ...")
                res = send_data(info)
                if not res:
                    break

        print_to_logger("kill")
        try:
            p_obj = psutil.Process(pid=process.pid)
            p_obj.send_signal(9)
            p_obj.kill()
            process.kill()
        except Exception as e:
            print_to_logger(str(e))
            pass
        queue.close()
        try:
            process.join()
        except:
            pass
        if call_id:
            cancel_invite_camera(cam_url, my_ip, port)

servers = []

mode_conf = {}




if __name__ == '__main__':
    import sys
    argv = sys.argv
    setproctitle.setproctitle("gbs_httpflv_server")
    try:
        from . import daemon
    except:
        pass
    # import daemon
    # daemon.daemon_start()
    # redis_url,run_port, my_ip = sys.argv[-3], sys.argv[-2], sys.argv[-1]
    #p = multiprocessing.Process(target=run_httpflv_server, args=(8001, my_ip))
    from gevent.server import StreamServer
    server = StreamServer(('', int(config.HTTPFLV_SERVER_PORT)), handle)
    servers = [server]
    server.start()
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)
    if argv[-1] == 'daemon':
        daemon.daemon_start()
    # daemon.daemon_start()
    server.serve_forever()
    # while 1:
    #     gevent.sleep(0.05)
    #     sys.stdout.flush()
    #p.start()