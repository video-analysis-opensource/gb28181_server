# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/4/13
from django.db import models
import time
from gbs_zxiat.settings import config
from urllib.parse import quote
import sys



class ServiceInfo(models.Model):
    # 存储服务实例， 如： 解码服务
    service_id = models.AutoField(primary_key=True)
    type = models.PositiveIntegerField(default=0)    #  1 解码服务
    ip = models.CharField(default='127.0.0.1', max_length=20)  # ip
    port = models.PositiveIntegerField(default=0)    # 端口
    addtime = models.PositiveIntegerField(default=0)  # 添加时间
    status = models.PositiveIntegerField(default=0)  # 0 离线  1在线
    status_uptime = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'service_info'
        unique_together = [('type', 'ip', 'port')]


class CustomSubDir(models.Model):
    # 目录树
    dir_code_id = models.CharField(max_length=30,primary_key=True)
    addtime = models.PositiveIntegerField(default=0)  # 添加时间
    name = models.CharField(max_length=200, unique=True)
    parent_id = models.CharField(max_length=30,default=0)  # 父ID

    class Meta:
        db_table = 'custom_sub_dir'


class GatewayInfo(models.Model):
    # 下级设备信息 (就是下级平台)
    _pk = models.AutoField(primary_key=True, db_column="pk")
    name = models.CharField(max_length=255, unique=True) # 名称
    code = models.CharField(max_length=32, default='', unique=True)
    ip = models.CharField(max_length=15, default='')    # 设备ip
    port = models.PositiveIntegerField(default=0)     # 设备端口
    limit_ipport = models.PositiveIntegerField(default=0)     # 设备端口
    manufacture = models.CharField(max_length=100, default='') # 生产厂家
    model =  models.CharField(max_length=250, default='')
    # is_wandev = models.PositiveIntegerField(default=0)    # 是否是公网设备。
    rtp_mode = models.PositiveIntegerField(default=0)   #  0 udp(默认)     1 tcp passive
    addtime = models.PositiveIntegerField(default=0)
    last_msg_time = models.PositiveIntegerField(default=0)  # 上次消息的时间。如果超过30秒，就认为离线
    heartbeat_time = models.PositiveIntegerField(default=0)  # 心跳时间。 （如果选择了nat穿透，心跳时间必须小于等于30秒）
    reg_time = models.PositiveIntegerField(default=0)  # 注册时间
    dir_code_id = models.CharField(max_length=30)  # 父目录id（通过该字段便于构建设备树）
    last_scan_catalog_time = models.PositiveIntegerField(default=0) # 最近一次的查询catalog的时间


    class Meta:
        db_table = 'gateway_info'
        unique_together = [('ip', 'port')]

    @property
    def is_online(self):
        _ = time.time() - 130
        if self.last_msg_time > _ or self.reg_time > _:
            return True
        else:
            return False

    @property
    def mode(self):
        if self.rtp_mode == 1:
            return 'TCP'
        else:
            return 'UDP'


class DeviceNodeInfo(models.Model):
    # 设备节点信息
    _pk = models.AutoField(primary_key=True,db_column="pk")
    code = models.CharField(max_length=50, default='') # 通道编码  用作主键
    gateway_code = models.CharField(max_length=30, default='')  # 所属网关
    is_dir = models.PositiveIntegerField(default=0)     #  0 设备  1 目录
    name = models.CharField(max_length=150, default='')    # 名字
    manufacture = models.CharField(max_length=150, default='')  # 制造商
    model = models.CharField(max_length=150, default='')   #型号
    parent_node_id = models.CharField(max_length=50, default='') # 父通道id
    civil_code = models.CharField(max_length=255, default='')
    block = models.CharField(max_length=255, default='')
    address = models.CharField(max_length=255, default='')
    ptz_type = models.CharField(max_length=255, default='')
    lng = models.CharField(max_length=50, default='')
    lat = models.CharField(max_length=50, default='')
    ip_address = models.CharField(max_length=50, default='')
    port = models.CharField(max_length=20, default='')
    is_online = models.PositiveIntegerField(default=0)  # 是否在线   1 在线   0 不在线
    update_time = models.PositiveIntegerField(default=0)
    addtime = models.PositiveIntegerField(default=0)
    raw_info = models.TextField() # 原始信息

    class Meta:
        db_table = 'device_node_info'
        unique_together = [('code', "gateway_code")]
        ordering = ["_pk"]

    @property
    def id(self):
        return "{}_{}".format(self.gateway_code, self.code)

    @property
    def parent_id(self):
        if self.parent_node_id == self.gateway_code or self.parent_node_id == '':
            return self.gateway_code
        else:
            return "{}_{}".format(self.gateway_code, self.parent_node_id)

    @property
    def online(self):
        if self.is_online and self.update_time > time.time() - 800:
            return True
        else:
            return False

    @property
    def httpflv_url(self):
        return 'http://{}:{}/?cam_url={}'.format(sys.django_host.split(":")[0], config.HTTPFLV_SERVER_PORT,
                                                 quote(self.cam_url)
                                                 )

    @property
    def wsflv_url(self):
        return 'ws://{}:{}/?cam_url={}'.format(sys.django_host.split(":")[0], config.HTTPFLV_SERVER_PORT,
                                                 quote(self.cam_url)
                                                 )

    @property
    def cam_url(self):
        return "gb28181://{}/{}".format(self.gateway_code, self.code)

    @property
    def ptz_type_cn(self):
        conf = {'0': '枪机', '1': '球机', '2': '半球', '3': '固定枪机', '4': '遥控枪机'}
        return conf.get(self.ptz_type, "枪机")


class DeviceNodeSnapshot(models.Model):
    # 快照信息
    id = models.AutoField(primary_key=True)
    channel_code = models.CharField(max_length=50, default='', unique=True)  # 通道编码
    snapshot_trytime = models.IntegerField(default=0)  # 尝试快照的时间

    gb_url = models.CharField(max_length=255, default='', unique=True)
    image = models.TextField()
    image_md5 = models.CharField(max_length=32)
    image_time = models.PositiveIntegerField(default=0) # 图像时间
    addtime = models.PositiveIntegerField(default=0) # 添加时间
    update_time = models.PositiveIntegerField(default=0)  # 更新时间

    class Meta:
        db_table = 'device_node_snapshot'


class SharedInfo(models.Model):
    # 国标共享
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120, default='')
    parent_sip_ip = models.CharField(max_length=30, default='')  # 国标ip
    parent_sip_port = models.PositiveIntegerField(default=0)  # 国标端口
    parent_gb_code = models.CharField(max_length=30, default='')  # 父级平台国标编码
    my_gb_code = models.CharField(max_length=30, default='')  # 我的国标编码
    share_node_info = models.TextField()    # 共享的通道信息
    reg_duration = models.PositiveIntegerField(default=0)  # 注册间隔
    heart_duration = models.PositiveIntegerField(default=0)  # 心跳间隔
    expire_times = models.PositiveIntegerField(default=0)  # 超时次数
    addtime = models.PositiveIntegerField(default=0)  # 添加时间戳
    update_time = models.PositiveIntegerField(default=0)  # 更新时间

    class Meta:
        db_table = 'shared_info'
        # unique_together = [('gb_ip','my_gb_code')]


class DecoderSceneInfo(models.Model):
    # 解码-  场景信息
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120, unique=True)
    start_time = models.CharField(max_length=20)
    end_time = models.CharField(max_length=20)
    dates = models.CharField(max_length=30)
    rule = models.CharField(max_length=50)
    addtime = models.PositiveIntegerField(default=0)
    update_time = models.PositiveIntegerField(default=0)  # 更新时间

    class Meta:
        db_table = 'decoder_scene_info'



class DecoderAlgoInfo(models.Model):
    # 解码- 算法信息
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=120, unique=True)
    urls = models.TextField(default='')
    addtime = models.PositiveIntegerField(default=0)
    update_time = models.PositiveIntegerField(default=0)  # 更新时间

    class Meta:
        db_table = 'decoder_algo_info'



class DecoderChannelAlgoConf(models.Model):
    # 解码  算法配置信息
    id = models.AutoField(primary_key=True)
    gb_url = models.CharField(max_length=255, default='')  # 国标url
    platform_name = models.CharField(max_length=50, default='')
    channel_code = models.CharField(max_length=30, default='')
    algo_name = models.CharField(max_length=120, default='')
    scene_name = models.CharField(max_length=120, default='')
    area_info = models.TextField(default='')
    addtime = models.PositiveIntegerField(default=0)
    update_time = models.PositiveIntegerField(default=0)  # 更新时间


    class Meta:
        db_table = 'decoder_device_algo_conf'
        unique_together = [('platform_name', 'channel_code',
                            'algo_name', 'scene_name')]



