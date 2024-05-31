# coding:utf-8
__author__ = "zkp"
# create by zkp on 2021/12/30
# 测试ps frame 转 h264
import bitstring
import traceback


def get_stream_type_from_ps(ps_frame_data:bytes):
    '获取流类型'
    try:
        bit_data = bitstring.BitArray(ps_frame_data)
        # ps流的头 一般都是  0x000001ba
        assert bit_data[:32].uint == 0x000001ba
        # 去掉ps头
        extend_len = bit_data[109:112].uint
        #print(extend_len)
        bit_data =  bit_data[(14*8+extend_len*8):]

        # 去掉 system header
        if bit_data[:32].uint == 0x000001bb:
            # 获取长度
            leng = bit_data[32:32+16]
            bit_data = bit_data[32+16+leng.uint*8:]
        #print(bit_data)
        # 去掉psm
        if bit_data[:32].uint == 0x000001bc:
            # 获取长度
            leng = bit_data[32:32 + 16]
            _program_stream_info_len = bit_data[64:80].uint
            _type = bit_data[80+8*_program_stream_info_len+16:80+8*_program_stream_info_len+16+16]
            if _type.uint == 0x24e0:
                return 'hevc'
            if _type.uint == 0x1be0:
                return 'h264'

        # 对于没有psm的直接通过裸流的前缀判断
        if bit_data[:28].uint == 0x000001e:
            pes_packet_len = bit_data[32:32 + 16].uint
            # print(len(bit_data.tobytes()), pes_packet_len)
            pes_data = bit_data[48: 48 + pes_packet_len * 8]
            # print(_data)
            #bit_data = bit_data[48 + pes_packet_len * 8:]
            # print(_data[0:2],_data[8:16].uint,_data[0:2].uint == 0b10)
            # if _data[0:2].uint == 0b10 and _data[8:16].uint == 0x80:
            # print(pes_data[0:2],pes_data[0:16],pes_data[8:16].uint)
            if pes_data[0:2].uint == 0b10:
                # 只对特定格式解析
                #i
                # print("pts",pts, _pts)
                extra_len = pes_data[16:24].uint
                # print('extra_len',extra_len)
                _h26x_bit_data = pes_data[24 + extra_len * 8:]
                #print(_h264_bit_data)
                _h26x_data = _h26x_bit_data.tobytes()
                if _h26x_data.startswith(b"\x00\x00\x00\x01\x02") or _h26x_data.startswith(b"\x00\x00\x00\x00\x01\x02"):
                    return 'hevc'
                else:
                    return 'h264'
    except Exception as e:
        print(str(e))
        pass
    #return 'h264'


def get_raw_stream_from_ps(ps_frame_data:bytes, with_pts=False):
    # ps 帧中提取 payload 。payload
    try:
        bit_data = bitstring.BitArray(ps_frame_data)
        # ps流的头 一般都是  0x000001ba
        assert bit_data[:32].uint == 0x000001ba
        # 去掉ps头
        extend_len = bit_data[109:112].uint
        bit_data =  bit_data[(14*8+extend_len*8):]
        # 去掉 system header
        if bit_data[:32].uint == 0x000001bb:
            # 获取长度
            leng = bit_data[32:32+16]
            bit_data = bit_data[32+16+leng.uint*8:]
        # 去掉psm
        if bit_data[:32].uint == 0x000001bc:
            # 获取长度
            leng = bit_data[32:32 + 16]
            #print(leng)
            bit_data = bit_data[32 + 16 + leng.uint * 8:]

        # 如果是pes包
        # pes 包的开头是 0x000001e
        #print("start handle  pes packet....")
        #print(bit_data)
        h264_data = b''
        pts = 0
        while 1:
            #print(bit_data)
            if bit_data[:28].uint == 0x000001e:
                #
                pes_packet_len = bit_data[32:32 + 16].uint
                #print(len(bit_data.tobytes()), pes_packet_len)
                pes_data = bit_data[48: 48+pes_packet_len*8]
                #print(_data)
                bit_data = bit_data[48+pes_packet_len*8:]
                #print(_data[0:2],_data[8:16].uint,_data[0:2].uint == 0b10)
                #if _data[0:2].uint == 0b10 and _data[8:16].uint == 0x80:
                #print(pes_data[0:2],pes_data[0:16],pes_data[8:16].uint)
                if  pes_data[0:2].uint == 0b10:
                    # 只对特定格式解析
                    if pts == 0:
                        _pts = pes_data[24: 64]
                        pts = (_pts[4:7] + _pts[8:16] +  _pts[16:23] + _pts[24:32] + _pts[32:39]).uint
                    #print("pts",pts, _pts)
                    extra_len = pes_data[16:24].uint
                    #print('extra_len',extra_len)
                    _h264_bit_data = pes_data[24 + extra_len * 8:]
                    _h264_data = _h264_bit_data.tobytes()
                    if _h264_data.startswith(b"\x00\x00\x00\x01\x09\xe0"):
                        _h264_data = _h264_data[6:]
                    #print('h264 data',_h264_bit_data)
                    h264_data += _h264_data

                    #continue
            else:
                break
            if not bit_data:
                break
        if not with_pts:
            return h264_data
        else:
            return h264_data, pts
    except Exception as e:
        pass
        #print(str(e))


if __name__ == '__main__':
    a = bitstring.BitArray(hex='0x000001ba44019cc9040100fa07feffff000001d2000001e013fa8c80072100673241fffd000000010201d000517f0810bcfe3d084faae25cba3291683c4a5d8613588919515d58ffacdb16415a485bd7b4ff5332e18ff5f151fd289d096884c5447172c190b47f8057545df4f87ac818851623ba6062126c20933aedc2')
    res = get_stream_type_from_ps(a.tobytes())
    print(res)