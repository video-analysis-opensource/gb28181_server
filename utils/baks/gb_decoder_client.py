# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/1/11
import bitstring
import gevent
from gevent.server import DatagramServer, StreamServer
import redis, time
import functools
import cv2, av
import copy
try:
    from . import ps_parser
except:
    import ps_parser


class RtcpClient(DatagramServer):

    def __init__(self, *args, client, **kwargs):
        DatagramServer.__init__(self, *args, **kwargs)
        self.client = client

    def handle(self, data:bytes, addr):
        data_array = bitstring.BitArray(data)
        print("rtcp_data",data_array)
        _type = data_array[8:16].uint
        if _type == 200:
            resp = self.get_recv_report(data, self.client.cycle_num, self.client.seq_num)
            print("rtcp_resp_data", bitstring.BitArray(resp))
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


class RTPDecoderClient(DatagramServer):
    # RTP解码类抽象
    timeout = 40
    def __init__(self, *args, only_keyframe:bool=True, image_num:int=1, **kwargs):
        # only_keyframe  是否是只要关键帧
        # image_num      想要获取的帧的数目， 如果想一直解码，可以设置一个很大的值。 如：1亿
        DatagramServer.__init__(self, *args, **kwargs)
        self.rtp_buff = []  # 用于缓冲RTP包
        self.codec = None
        self.stopped = False
        self.only_keyframe = only_keyframe  # 是否是只要关键帧
        self.waite_image_num = image_num
        self.rtcp_client = RtcpClient(":%s" % (int(self.address[1]) + 1), client=self)


        self.rtp_greenlet = gevent.spawn(self.rtp_frame_handle)
        self._packet_num = 0  # 记录当前接收到的包的数量。
        self._kill_func = None
        self.image_handle = None
        self.last_frame = None
        self._last_frame_time = 0
        self._start_time = time.time()
        self._frame_num = 0
        self._rtp_end_buff = {}
        self.seq_num = 0
        self.cycle_num = 0



    def handle(self, data, address):
        self._packet_num += 1
        bit_data = bitstring.BitArray(data)
        try:
            pt = bit_data[9:16]
            cc = bit_data[4:8]
            is_end = bit_data[8]
            seq_num = bit_data[16:32].uint
            # 对海康nvr上报的包进行特殊处理。 其没有对is_end进行标识，需要手动处理下。
            if bit_data[96+cc.uint*8:96+cc.uint*8+32].uint == 0x000001ba:
                _is_start = 1
            else:
                _is_start = 0
        except Exception as e:
            #print(str(e))
            pass
        else:
            if self.seq_num:
                if seq_num - self.seq_num > 1:
                    print("丢包###############", seq_num, self.seq_num)
            if seq_num == 65535:
                self.cycle_num += 1
            self.seq_num = seq_num
            if pt.uint in (96, 97, 98):
                rtp_data = bit_data[96:].tobytes()
                if rtp_data:
                    if _is_start:
                        self._rtp_end_buff[(seq_num-1) if seq_num !=0  else 65535] = 1
                    self.rtp_buff.append((seq_num, is_end, rtp_data))


    def packet_handle(self, h264_frame_bytes:bytes):
        "包处理函数"
        if self.codec:
            try:
                packets = self.codec.parse(h264_frame_bytes)
                for packet in packets:
                    frames = self.codec.decode(packet)
                    for frame in frames:
                        # 获取图像
                        print("frame", frame,'~~')
                        img = frame.to_ndarray(format='bgr24').copy()
                        self.last_frame = img.copy()
                        self._frame_num +=1
                        self._last_frame_time = int(time.time())

                if self._frame_num <= self.waite_image_num:
                    if self.image_handle:
                        try:
                            self.image_handle(img)
                        except:
                            pass
            except Exception as e:
                print(str(e)),"xxx"


    def set_image_handle(self, handle_function):
        self.image_handle = handle_function


    def set_kill_function(self, function):
        self._kill_func = function


    def rtp_frame_handle(self):
        # rtp 组包
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
        stream_type = None
        while 1:
            if self._packet_num < 100:
                # 当接收到的包超过100个之后 再开始进入数据处理逻辑
                gevent.sleep(0.1)
                continue
            if self.stopped:
                return
            gevent.sleep(0.6)
            self.rtp_buff.sort(key=functools.cmp_to_key(cmp))
            last_end = 0
            for index,data in enumerate(copy.deepcopy(self.rtp_buff[:-30])):
                pack_nu, is_end, raw_data = data
                if is_end or self._rtp_end_buff.get(pack_nu, 0):
                    try:
                        del self._rtp_end_buff[pack_nu]
                    except:
                        pass

                    frame_data = b"".join([i[-1] for i in self.rtp_buff[(last_end or -1 )+1:index + 1]
                                           if not i[-1].startswith(b"\x00\x00\x01\xbd")])
                    last_end = index
                    if frame_data.startswith(b"\x00\x00\x01\xba"):
                        if stream_type == None:
                            stream_type = ps_parser.get_stream_type_from_ps(frame_data) or 'h264'
                            print("流类型为", stream_type)
                            self.codec = av.CodecContext.create(stream_type, "r")
                            print("self.codec",self.codec)
                            if self.only_keyframe:
                                self.codec.skip_frame = 'NONKEY'

                        h26x_data = ps_parser.get_raw_stream_from_ps(frame_data)
                        #print('h26x_data',len(h26x_data),bitstring.BitArray(h26x_data)[:1024])
                        if h26x_data:
                            if self.only_keyframe:
                                # 判断是否是关键帧
                                _h26x_head_data = bitstring.BitArray(h26x_data[:15])
                                if _h26x_head_data[24:32].uint == 0x01:
                                    frame_type = _h26x_head_data[32:40]
                                elif _h26x_head_data[16:24].uint == 0x01:
                                    frame_type = _h26x_head_data[24:32]
                                else:
                                    frame_type = bitstring.BitArray(b'\x00')
                                if stream_type == 'h264' and frame_type.uint in (0x65, 0x67, 0x68, 0x27, 0x25, 0x28):
                                    # 对于h264关键帧的判断
                                    self.packet_handle(h26x_data)
                                if stream_type == 'hevc' and frame_type.uint in (0x40, 0x42, 0x44, 0x4e, 0x26):
                                    # 对于h265关键帧的判断
                                    self.packet_handle(h26x_data)

                            else:
                                self.packet_handle(h26x_data)

            else:
                self.rtp_buff = self.rtp_buff[(last_end or -1 ) + 1:]


    def stop_serv(self):
        self.stop()
        self.rtcp_client.stop()
        self.stopped = True
        try:
            self.codec.close()
        except:
            pass
        gevent.kill(self.rtp_greenlet)


    def start_serv(self):
        self.start()
        self.rtcp_client.start()


    def wait_image(self):
        # 等待图像， 最多N秒。 如果N秒获取不到，则返回None
        while 1:
            gevent.sleep(1)
            # 判断是否
            try:
                killed =self._kill_func and self._kill_func()
            except Exception as e:
                pass
            else:
                if killed:
                    self.stop()
                    self.stopped = True
                    print("Kill the Client!")
                    return self._frame_num
            if self._last_frame_time == 0:
                if time.time() - self._start_time > self.timeout:
                    self.stop()
                    self.stopped = True
                    print("Wait first frame Timeout! ", self.timeout)
                    return self._frame_num
            else:
                if time.time() - self._last_frame_time > self.timeout:
                    self.stop()
                    self.stopped = True
                    print("Wait next frame Timeout!" ,self.timeout)
                    return self._frame_num
            if self._frame_num  >= self.waite_image_num:
                print("Get %s Frame Finished!" % self.waite_image_num)
                self.stop()
                self.stopped = True
                return self._frame_num
        return self._frame_num


    def __del__(self):
        # 相关清理操作
        try:
            self.codec.close()
        except:
            pass
        del self.last_frame
        try:
            self.stop_serv()
        except:
            pass


class TCPRTPDecoderClient(object):
    "TCP模式接收RTP流"
    timeout = 40
    def __init__(self, *args, only_keyframe:bool=True, image_num:int=1, **kwargs):
        self.waite_image_num = image_num
        self._frame_num = 0
        self.only_keyframe = only_keyframe
        self._image_handle = None
        self._kill_func = None
        self.codec = None
        self._start_time = time.time()
        self._last_frame_time = 0
        self.last_frame = None
        self.stopped = False

        def tcp_handle(sock, addr):
            stream_type = None
            #codec = None
            def packet_handle(h26x_frame_bytes: bytes, _time: int = None):
                "包处理函数"
                if self.codec:
                    try:
                        packets = self.codec.parse(h26x_frame_bytes)
                        for packet in packets:
                            frames = self.codec.decode(packet)
                            for frame in frames:
                                # 获取图像
                                print("frame", frame, '~~')
                                img = frame.to_ndarray(format='bgr24').copy()
                                self.last_frame = img.copy()
                                self._frame_num += 1
                                self._last_frame_time = int(time.time())

                        if self._frame_num <= self.waite_image_num:
                            if self._image_handle:
                                try:
                                    self._image_handle(img)
                                except:
                                    pass
                    except Exception as e:
                        print(str(e)), "xxx"

            buff = b''
            last_data_time = time.time()
            rtp_data = b''
            while 1:
                if sock.closed or time.time() - last_data_time > 8 or self.stopped:
                    # 如果socket被关闭 或者 超过8秒未获取到数据
                    print("end.....")
                    break
                try:
                    data = sock.recv(4096)
                except ConnectionResetError as e:
                    break
                except Exception as e :
                    print("recv exception",str(e))
                    gevent.sleep(0.003)
                    continue

                if not data:
                    gevent.sleep(0.003)
                    continue
                else:
                    last_data_time = time.time()
                buff += data
                while 1:
                    if not buff:
                        break
                    _len = bitstring.BitArray(buff[:2]).uint
                    if len(buff) >= _len + 2:
                        rtp_frame_data = buff[2:2 + _len]
                        buff = buff[2 + _len:]
                        bit_data = bitstring.BitArray(rtp_frame_data[:12])
                        try:
                            pt = bit_data[9:16]
                            cc = bit_data[4:8]
                            is_end = bit_data[8]
                            seq_num = bit_data[16:32].uint
                            timestamp = bit_data[32:64].uint
                            # print(seq_num,len(data), bit_data[:512+64], is_end, timestamp)
                        except Exception as e:
                            # print(str(e))
                            pass
                        else:
                            rtp_data += rtp_frame_data[12:]
                            if is_end:
                                ps_frame_data = rtp_data
                                rtp_data = b''
                                # print(time.time(), bitstring.BitArray(ps_frame_data)[:1024],
                                #       timestamp,"ps_len",len(ps_frame_data))
                                if ps_frame_data.startswith(b"\x00\x00\x01\xba"):
                                    if stream_type == None:
                                        stream_type = ps_parser.get_stream_type_from_ps(ps_frame_data) or 'h264'
                                        print("流类型为", stream_type)
                                        self.codec = av.CodecContext.create(stream_type, "r")
                                        print("codec", self.codec)
                                        if self.only_keyframe:
                                            self.codec.skip_frame = 'NONKEY'

                                    res = ps_parser.get_raw_stream_from_ps(ps_frame_data, with_pts=True)
                                    if res and res[0]:
                                        h26x_data, pts = res
                                        packet_handle(h26x_data, pts)
                            else:
                                pass
                    else:
                        break

        self.stream_server = StreamServer(*args, handle=tcp_handle, **kwargs)


    def set_image_handle(self, handle_function):
        self._image_handle = handle_function


    def start_serv(self):
        self.stream_server.start()

    def stop_serv(self):
        try:
            self.stream_server.stop_accepting()
        except:
            pass
        try:
            self.stream_server.stop()
        except:
            pass
        self.stopped = True

    def set_kill_function(self, function):
        self._kill_func = function

    def wait_image(self):
        while 1:
            gevent.sleep(0.2)
            # 判断是否
            try:
                killed =self._kill_func and self._kill_func()
            except Exception as e:
                pass
            else:
                if killed:
                    self.stop_serv()
                    self.stopped = True
                    print("Kill the Client!")
                    return self._frame_num
            if self._last_frame_time == 0:
                if time.time() - self._start_time > self.timeout:
                    self.stop_serv()
                    self.stopped = True
                    print("Wait first frame Timeout! ", self.timeout)
                    return self._frame_num
            else:
                if time.time() - self._last_frame_time > self.timeout:
                    self.stop_serv()
                    self.stopped = True
                    print("Wait next frame Timeout!" ,self.timeout)
                    return self._frame_num
            if self._frame_num  >= self.waite_image_num:
                print("Get %s Frame Finished!" % self.waite_image_num)
                self.stop_serv()
                self.stopped = True
                return self._frame_num
        return self._frame_num


    def __del__(self):
        try:
            self.codec.close()
        except:
            pass
        try:
            self.stop_serv()
        except:
            pass


if __name__ == '__main__':
    from gevent.monkey import patch_all;patch_all(thread=False, subprocess=False)
    aa = TCPRTPDecoderClient(":3333", only_keyframe=False, image_num=10)
    aa.start_serv()
    aa.wait_image()