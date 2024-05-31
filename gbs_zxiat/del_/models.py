# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/4/13
from django.db import models


class ServiceInfo(models.Model):
    # 存储服务实例， 如： 流媒体及转发服务  快照服务 解码服务
    service_id = models.AutoField(primary_key=True)
    type = models.PositiveIntegerField(default=0)    # 1 流媒体及流转发服务  2 快照服务   3 解码服务
    ip = models.IPAddressField(default='127.0.0.1') # ip
    port = models.PositiveIntegerField(default=0)  # 端口
    addtime = models.PositiveIntegerField(default=0)  # 添加时间
    status = models.PositiveIntegerField(default=0)  # 0 离线  1在线
    status_uptime = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'service_info'
        unique_together = [('type', 'ip', 'port')]


class CustomSubDir(models.Model):
    #
    dir_code_id = models.AutoField(primary_key=True)
    addtime = models.PositiveIntegerField(default=0)  # 添加时间
    name = models.CharField(max_length=200, unique=True)
    parent_id = models.PositiveIntegerField(default=0)  # 父ID

    class Meta:
        db_table = 'custom_sub_dir'


class GatewayInfo(models.Model):
    # 下级设备信息 (就是下级平台)
    node_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True) # 名称
    code = models.CharField(max_length=20, default='')
    ip = models.CharField(max_length=15, default='')  # ip
    port = models.PositiveIntegerField(default=0)  # 端口
    manufacture = models.CharField(max_length=100, default='') # 生产厂家
    rtp_mode = models.PositiveIntegerField(default=0)   #  0 udp(默认)     1 tcp passive
    sip_server = models.PositiveIntegerField(default=0)  # 信令服务器
    preview_server = models.PositiveIntegerField(default=0)  # 快照服务
    stream_forward_servers = models.CharField(max_length=300) #  流媒体及流转发服务
    decoder_servers  = models.CharField(max_length=300) # 解码服务
    addtime = models.PositiveIntegerField(default=0)
    last_msg_time = models.PositiveIntegerField(default=0)  # 上次消息的时间。如果超过30秒，就认为离线
    heartbeat_time = models.PositiveIntegerField(default=0)  # 心跳时间。
    reg_time = models.PositiveIntegerField(default=0)  # 注册时间
    dir_code_id = models.PositiveIntegerField(default=0)  # 父目录id（通过该字段便于构建设备树）

    class Meta:
        db_table = 'gateway_info'
        unique_together = [('ip', 'port')]


class DeviceNodeInfo(models.Model):
    # 设备节点信息
    node_id = models.CharField(max_length=50, default='', primary_key=True) # 通道编码  用作主键
    # gb_url = models.CharField(max_length=255, default='', unique=True)
    #platform_name = models.PositiveIntegerField(default=0)   # 平台id
    node_type = models.PositiveIntegerField(default=0)    # 是否是目录  0 设备 1 设备目录  2 手工添加的目录
    gateway_node_id = models.PositiveIntegerField(default=0)      # 所属下级设备
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
        unique_together = [('gb_ip','gb_port')]


class KvSettingInfo(models.Model):
    # kv配置项
    k = models.CharField(max_length=100, primary_key=True)
    v = models.TextField(default='')
    comment = models.CharField(default='', max_length=255)
    addtime = models.PositiveIntegerField(default=0)
    update_time = models.PositiveIntegerField(default=0)  # 更新时间

    class Meta:
        db_table = 'kv_setting_info'


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



