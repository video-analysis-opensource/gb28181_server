# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/1/17
# httpflv流媒体转发核心逻辑
import datetime
import logging
import string
import redis
from gevent.monkey import patch_all;patch_all()
import gevent
from gevent.pool import  Pool
from urllib import parse
import socket,random,sys, os, psutil
import urllib.parse
import setproctitle
import hashlib, base64, struct, time
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_PATH)
sys.path.append(os.path.join(os.path.dirname(BASE_PATH)))
import config
import requests
import os
try:
    import xmltodict,orm_tool, color_print, get_logger, daemon, ps_parser, process_task
except:
    from . import xmltodict,orm_tool, color_print, get_logger, daemon, ps_parser, process_task


os.system("mkdir -p %s" % config.WORK_DIR)
log_dir = os.path.join(config.WORK_DIR, "logs")
os.system("mkdir -p %s" % log_dir)
# log_obj = get_logger.get_logger(os.path.join(log_dir,"gb_httpflv_server.log"), backupCount=10)


def print_to_logger(*args):
    file_name = os.path.join(log_dir, f"gb_httpflv_server-{datetime.datetime.now().strftime('%Y%m%d')}.log")
    now = datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds')
    try:
        msg = " ".join([str(i) for i in args ])
        with open(file_name, "a+") as f:
            f.write(f"[{now}: INFO]:{msg}\n")
    except:
        pass

print_to_logger("开始启动服务...")


def detect_one_tcp_port(start_port=25000):
    flag = socket.SOCK_STREAM
    for i in range(start_port + random.randrange(0, 5000, 10), 30000, 2):
        try:
            s = socket.socket(socket.AF_INET, flag)
            s.bind(('0.0.0.0', i))
            s.close()
        except:
            try:
                s.close()
            except:
                pass
        else:
            return i


def av_function(cam_url, queue_key, port, redis_url, out_size):
    import time, os, datetime,traceback,av
    av.logging.set_level(av.logging.CRITICAL)
    def print_to_logger(*args):
        file_name = os.path.join(log_dir, f"gb_httpflv_decoder-{datetime.datetime.now().strftime('%Y%m%d')}.log")
        now = datetime.datetime.now().isoformat(sep=' ', timespec='milliseconds')
        try:
            msg = " ".join([str(i) for i in args])
            with open(file_name, "a+") as f:
                f.write(f"[{now}: INFO]:{msg}\n")
        except:
            pass
    print_to_logger("start av_function", time.time())
    from gevent.monkey import patch_all;patch_all()
    from gevent.server import StreamServer
    import redis
    import bitstring
    import psutil

    redis_conn = redis.Redis.from_url(redis_url)
    redis_conn.delete(queue_key)

    class FileObj(object):
        def __init__(self, name):
            self.name = name
            self.key = queue_key
            self.buff = b''
            self.last_time = time.time()

        def write(self, info: bytes):
            #self.times += 1
            _t = time.time()
            self.buff += info
            if _t - self.last_time > 0.3: # 超过0.3秒
                try:
                    #self.file.write(info)
                    #self.queue.put_nowait(self.buff)
                    redis_conn.rpush(self.key, self.buff)
                except Exception as e:
                    print_to_logger("put failed")
                    print_to_logger(traceback.format_exc())
                self.buff = b''
                self.last_time = _t
                # sys.exit()

        def qsize(self):
            try:
                #return self.queue.qsize()
                return redis_conn.llen(self.key)
            except:
                return 0

    # tcp 模式
    def tcp_handle(sock, addr):
        print_to_logger("httpflv_av_function, tcp_handle", sock, addr)
        stream_type = None
        codec = None
        file_name = ",".join(random.sample(string.ascii_letters + '0123456789', 10))
        file_obj = FileObj(f"{file_name}.flv")
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
                        #print_to_logger(packet)
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
                        err = av.logging.get_last_error()
                        #print_to_logger(err)
                        # if err[0] != 0 and err[0] != self.last_err:
                        #     print(packet, err)
                        #     self.last_err = err[0]
                        #     continue
                        if len(frames):
                            # print(packet,_time, self._last_pts)
                            # else:
                                # 对x265编码的packet。 先编码再mux
                            for frame in frames:
                                frame = frame.reformat(*out_size)
                                # print_to_logger("frame", frame)
                                try:
                                    qsize = file_obj.qsize()
                                    #print_to_logger("qsize", qsize,  "port", port, "frame" ,frame)
                                    _out_stream.width, _out_stream.height = out_size#config.HTTPFLV_OUTPUT_SIZE
                                    _packets = _out_stream.encode(frame)
                                    if qsize >= 100 :
                                        if not frame.key_frame:
                                            continue
                                    for _p in _packets:
                                        _output.mux(_p)
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
            try:
                with gevent.Timeout(2):
                    data = sock.recv(1024*1024*4)
            except (Exception, BaseException, gevent.Timeout) as e:
                print("sock recv timeout 2")
                data = b''
            #print(time.time(), len(data))
            #continue
            if sock.closed or time.time() - last_data_time > 12:
                # 如果socket被关闭 或者 超过12秒未获取到数据
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
                    bit_data = bitstring.BitArray(rtp_frame_data[:12])
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
                        rtp_data = rtp_frame_data[12:]
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
    client.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024*8)
    import setproctitle
    setproctitle.setproctitle("gbs_httpflv_decoder %s" % cam_url)
    print_to_logger("client start", client,  time.time())
    redis_conn.set(f"httpflv_flag_{cam_url}_{port}", 1, 10)
    client.serve_forever()


# my_ip = config.HTTPFLV_SERVER_IP
my_recv_stream_ip = config.HTTPFLV_RECV_RTP_IP


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
            cam_url = query_dict['cam_url'].strip(".flv").replace("11.4.14.1:5061",
                                  '41011001002000000010')
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


        port = detect_one_tcp_port()
        queue_key = f"httpflv_queue_{cam_url}_{port}"
        redis_conn = redis.Redis.from_url(config.REDIS_URL)
        task_id = process_task.run_task(av_function, (cam_url, queue_key, port,
                                                      config.REDIS_URL, config.HTTPFLV_OUTPUT_SIZE))
        try:
            with gevent.Timeout(1):
                for i in range(100):
                    gevent.sleep(0.05)
                    if redis_conn.get(f"httpflv_flag_{cam_url}_{port}"):
                        break
        except (gevent.Timeout, BaseException) as _e:
            pass
        call_id = invite_camera(cam_url, my_recv_stream_ip, port)
        print_to_logger("invite_camera...", time.time(), "call_id", call_id, "mypid", os.getpid())

        last_data_time = time.time()
        print_to_logger("last_data_time", last_data_time)
        while 1:
            #print_to_logger("port", port, "loop", time.time())
            # 如果超过1.5分钟未获取到数据
            if time.time() - last_data_time > 90:
                print_to_logger("last data time > 90 s  end .....", cam_url, os.getpid(), os.getppid())
                break
            try:
                info = redis_conn.lpop(queue_key)
                assert len(info) > 0
                # gevent.sleep(0.001)
            except Exception as e:
                gevent.sleep(0.1)
            else:
                last_data_time = time.time()
                #print_to_logger("send ...", time.time())
                if not is_websocket:
                    try:
                        sock.sendall(info)
                    except Exception as e:
                        print_to_logger("sock.sendall error", str(e))
                        break
                else:
                    header = Header.encode_header(True, 0x02, b'', len(info), 0)
                    try:
                        sock.sendall(header+info)
                    except Exception as e:
                        print_to_logger("sock.sendall error", str(e))
                        break

                # print_to_logger("send finished!..", time.time())
        cancel_invite_camera(cam_url, my_recv_stream_ip, port)
        redis_conn.close()
        print_to_logger("kill")
        try:
            with open(f"/tmp/process_task/pids/{task_id}", "r") as f:
                worker_pid = int(f.read())
        except:
            print_to_logger("cant find pid!")
        else:
            try:
                p_obj = psutil.Process(pid=worker_pid)
                p_obj.send_signal(9)
                p_obj.kill()
            except Exception as e:
                print_to_logger(str(e))
                pass
            try:
                p_obj.wait()
            except:
                pass
            #if call_id:


if __name__ == '__main__':
    import sys, psutil
    argv = sys.argv
    setproctitle.setproctitle("gbs_httpflv_server")
    try:
        from . import daemon
    except:
        pass
    for i in psutil.Process(pid=1).children(True):
        try:
            if  i.name().startswith("gbs_httpflv_decoder"):
                print(i)
                try:
                    i.kill()
                    i.send_signal(9)
                except:
                    pass
                try:
                    i.wait()
                except:
                    pass
        except:
            pass
    daemon.redirect_output(os.path.join(config.WORK_DIR, "deamon.out"))
    pool = Pool(1000)
    from gevent.server import StreamServer
    server = StreamServer(('', int(config.HTTPFLV_SERVER_PORT)), handle, spawn=pool)
    server.start()
    server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024*1024*8)
    if argv[-1] == 'daemon':
        daemon.daemon_start()
    print('httpflv_server start ..', time.time())
    server.serve_forever()