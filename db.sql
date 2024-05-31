-- MySQL dump 10.13  Distrib 5.7.10, for osx10.11 (x86_64)
--
-- Host: 192.168.220.80    Database: gbs_zxiat
-- ------------------------------------------------------
-- Server version	8.0.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `1_del_kv_setting_info`
--

DROP TABLE IF EXISTS `1_del_kv_setting_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `1_del_kv_setting_info` (
  `k` varchar(100) NOT NULL,
  `v` longtext NOT NULL,
  `comment` varchar(255) NOT NULL,
  `addtime` int unsigned NOT NULL,
  `update_time` int unsigned NOT NULL,
  PRIMARY KEY (`k`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `1_del_kv_setting_info`
--

LOCK TABLES `1_del_kv_setting_info` WRITE;
/*!40000 ALTER TABLE `1_del_kv_setting_info` DISABLE KEYS */;
INSERT INTO `1_del_kv_setting_info` VALUES ('s','v','2',323,111);
/*!40000 ALTER TABLE `1_del_kv_setting_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=61 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add log entry',1,'add_logentry'),(2,'Can change log entry',1,'change_logentry'),(3,'Can delete log entry',1,'delete_logentry'),(4,'Can view log entry',1,'view_logentry'),(5,'Can add permission',2,'add_permission'),(6,'Can change permission',2,'change_permission'),(7,'Can delete permission',2,'delete_permission'),(8,'Can view permission',2,'view_permission'),(9,'Can add group',3,'add_group'),(10,'Can change group',3,'change_group'),(11,'Can delete group',3,'delete_group'),(12,'Can view group',3,'view_group'),(13,'Can add user',4,'add_user'),(14,'Can change user',4,'change_user'),(15,'Can delete user',4,'delete_user'),(16,'Can view user',4,'view_user'),(17,'Can add content type',5,'add_contenttype'),(18,'Can change content type',5,'change_contenttype'),(19,'Can delete content type',5,'delete_contenttype'),(20,'Can view content type',5,'view_contenttype'),(21,'Can add session',6,'add_session'),(22,'Can change session',6,'change_session'),(23,'Can delete session',6,'delete_session'),(24,'Can view session',6,'view_session'),(25,'Can add service info',7,'add_serviceinfo'),(26,'Can change service info',7,'change_serviceinfo'),(27,'Can delete service info',7,'delete_serviceinfo'),(28,'Can view service info',7,'view_serviceinfo'),(29,'Can add platform info',8,'add_platforminfo'),(30,'Can change platform info',8,'change_platforminfo'),(31,'Can delete platform info',8,'delete_platforminfo'),(32,'Can view platform info',8,'view_platforminfo'),(33,'Can add channel info',9,'add_channelinfo'),(34,'Can change channel info',9,'change_channelinfo'),(35,'Can delete channel info',9,'delete_channelinfo'),(36,'Can view channel info',9,'view_channelinfo'),(37,'Can add channel snapshot',10,'add_channelsnapshot'),(38,'Can change channel snapshot',10,'change_channelsnapshot'),(39,'Can delete channel snapshot',10,'delete_channelsnapshot'),(40,'Can view channel snapshot',10,'view_channelsnapshot'),(41,'Can add shared info',11,'add_sharedinfo'),(42,'Can change shared info',11,'change_sharedinfo'),(43,'Can delete shared info',11,'delete_sharedinfo'),(44,'Can view shared info',11,'view_sharedinfo'),(45,'Can add kv setting info',12,'add_kvsettinginfo'),(46,'Can change kv setting info',12,'change_kvsettinginfo'),(47,'Can delete kv setting info',12,'delete_kvsettinginfo'),(48,'Can view kv setting info',12,'view_kvsettinginfo'),(49,'Can add decoder scene info',13,'add_decodersceneinfo'),(50,'Can change decoder scene info',13,'change_decodersceneinfo'),(51,'Can delete decoder scene info',13,'delete_decodersceneinfo'),(52,'Can view decoder scene info',13,'view_decodersceneinfo'),(53,'Can add decoder algo info',14,'add_decoderalgoinfo'),(54,'Can change decoder algo info',14,'change_decoderalgoinfo'),(55,'Can delete decoder algo info',14,'delete_decoderalgoinfo'),(56,'Can view decoder algo info',14,'view_decoderalgoinfo'),(57,'Can add decoder channel algo conf',15,'add_decoderchannelalgoconf'),(58,'Can change decoder channel algo conf',15,'change_decoderchannelalgoconf'),(59,'Can delete decoder channel algo conf',15,'delete_decoderchannelalgoconf'),(60,'Can view decoder channel algo conf',15,'view_decoderchannelalgoconf');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$150000$riVAU758sl5z$wZ9H5WzPYbO7m9ByyrxBZO13+rAwyS8Dv5QAQ75X1pg=','2022-06-07 15:04:43.483861',1,'admin','','ss','18749679769@163.com',1,1,'2022-04-15 11:00:37.638399');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `channel_snapshot`
--

DROP TABLE IF EXISTS `channel_snapshot`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `channel_snapshot` (
  `id` int NOT NULL AUTO_INCREMENT,
  `image` longtext NOT NULL,
  `image_md5` varchar(32) NOT NULL,
  `image_time` int unsigned NOT NULL,
  `addtime` int unsigned NOT NULL DEFAULT '0',
  `update_time` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `channel_snapshot`
--

LOCK TABLES `channel_snapshot` WRITE;
/*!40000 ALTER TABLE `channel_snapshot` DISABLE KEYS */;
/*!40000 ALTER TABLE `channel_snapshot` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `custom_sub_dir`
--

DROP TABLE IF EXISTS `custom_sub_dir`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `custom_sub_dir` (
  `dir_code_id` varchar(30) NOT NULL,
  `addtime` int unsigned NOT NULL DEFAULT '0',
  `name` varchar(100) NOT NULL DEFAULT '',
  `parent_id` varchar(30) NOT NULL DEFAULT '',
  PRIMARY KEY (`dir_code_id`),
  UNIQUE KEY `custom_sub_dir_name_uindex` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COMMENT='自定义子目录';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `custom_sub_dir`
--

LOCK TABLES `custom_sub_dir` WRITE;
/*!40000 ALTER TABLE `custom_sub_dir` DISABLE KEYS */;
INSERT INTO `custom_sub_dir` VALUES ('11111111110000000000',1653363341,'2','11111111110000000007'),('11111111110000000007',1653363336,'12225','00000000000000000000'),('11111111110000000010',1653465811,'1','11111111110000000000'),('11111111110000000011',1653465818,'333','11111111110000000010'),('11111111110000000012',1653465828,'12','11111111110000000011'),('11111111110000000013',1653465835,'13','11111111110000000012'),('11111111110000000014',1653465859,'14','11111111110000000013'),('12132344535465675765',1654583190,'1212121','23324354354655767868'),('23324354354655767868',1654582942,'测试','00000000000000000000'),('32322222222222222222',1654586886,'2324王企鹅多','12132344535465675765');
/*!40000 ALTER TABLE `custom_sub_dir` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `decoder_algo_info`
--

DROP TABLE IF EXISTS `decoder_algo_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `decoder_algo_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `urls` longtext NOT NULL,
  `addtime` int unsigned NOT NULL DEFAULT '0',
  `update_time` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `decoder_algo_info`
--

LOCK TABLES `decoder_algo_info` WRITE;
/*!40000 ALTER TABLE `decoder_algo_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `decoder_algo_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `decoder_channel_algo_conf`
--

DROP TABLE IF EXISTS `decoder_channel_algo_conf`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `decoder_channel_algo_conf` (
  `id` int NOT NULL AUTO_INCREMENT,
  `platform_name` varchar(50) NOT NULL,
  `channel_code` varchar(30) NOT NULL,
  `algo_name` varchar(120) NOT NULL,
  `scene_name` varchar(120) NOT NULL,
  `area_info` longtext NOT NULL,
  `addtime` int unsigned NOT NULL DEFAULT '0',
  `update_time` int unsigned NOT NULL DEFAULT '0',
  `gb_url` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `decoder_channel_algo_con_platform_name_channel_co_f50f630c_uniq` (`platform_name`,`channel_code`,`algo_name`,`scene_name`),
  KEY `decoder_channel_algo_conf_gb_url_index` (`gb_url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `decoder_channel_algo_conf`
--

LOCK TABLES `decoder_channel_algo_conf` WRITE;
/*!40000 ALTER TABLE `decoder_channel_algo_conf` DISABLE KEYS */;
/*!40000 ALTER TABLE `decoder_channel_algo_conf` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `decoder_scene_info`
--

DROP TABLE IF EXISTS `decoder_scene_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `decoder_scene_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `start_time` varchar(20) NOT NULL,
  `end_time` varchar(20) NOT NULL,
  `dates` varchar(30) NOT NULL,
  `rule` varchar(50) NOT NULL,
  `addtime` int unsigned NOT NULL,
  `update_time` int unsigned NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `decoder_scene_info`
--

LOCK TABLES `decoder_scene_info` WRITE;
/*!40000 ALTER TABLE `decoder_scene_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `decoder_scene_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `device_node_info`
--

DROP TABLE IF EXISTS `device_node_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `device_node_info` (
  `pk` int NOT NULL AUTO_INCREMENT,
  `code` varchar(50) NOT NULL DEFAULT '' COMMENT '所属的网关设备',
  `gateway_code` varchar(50) NOT NULL DEFAULT '',
  `is_dir` int unsigned NOT NULL DEFAULT '0',
  `name` varchar(150) NOT NULL,
  `manufacture` varchar(150) NOT NULL,
  `model` varchar(150) NOT NULL,
  `parent_node_id` varchar(50) NOT NULL,
  `civil_code` varchar(255) NOT NULL,
  `block` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `ptz_type` varchar(255) NOT NULL,
  `lng` varchar(50) NOT NULL,
  `lat` varchar(50) NOT NULL,
  `ip_address` varchar(50) NOT NULL,
  `port` varchar(20) NOT NULL,
  `is_online` int unsigned NOT NULL DEFAULT '0',
  `update_time` int unsigned NOT NULL DEFAULT '0',
  `addtime` int unsigned NOT NULL DEFAULT '0',
  `snapshot_trytime` int NOT NULL DEFAULT '0',
  `raw_info` longtext NOT NULL,
  PRIMARY KEY (`pk`),
  UNIQUE KEY `device_node_info_code_gateway_code_uindex` (`code`,`gateway_code`),
  KEY `device_node_info_gateway_code_is_dir_index` (`gateway_code`,`is_dir`),
  KEY `device_node_info_name_index` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb3 COMMENT='节点信息';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `device_node_info`
--

LOCK TABLES `device_node_info` WRITE;
/*!40000 ALTER TABLE `device_node_info` DISABLE KEYS */;
INSERT INTO `device_node_info` VALUES (1,'34020000001320000217','34020000001320000217',0,'aaaaassss','JCO','V1700N-N','','','','','3','','','install.addr','',1,1654586991,1653464389,0,'<Item>\r\n<DeviceID>34020000001320000217</DeviceID>\r\n<Name>aaaaassss</Name>\r\n<Manufacturer>JCO</Manufacturer>\r\n<Model>V1700N-N</Model>\r\n<Owner>Onwer</Owner>\r\n<CivilCode>3402000000</CivilCode>\r\n<Address>install.addr</Address>\r\n<Parental>0</Parental>\r\n<ParentID>34020000001320000217</ParentID>\r\n<SafetyWay>0</SafetyWay>\r\n<RegisterWay>1</RegisterWay>\r\n<Secrecy>0</Secrecy>\r\n<Status>ON</Status>\r\n</Item>'),(2,'34020000001310000002','44010200492000000120',0,'IP:192.168.1.177 -球机','Dahua','DH-NVR504-I','00000000080000000008','','','','1','0.0','0.0','192.168.1.177','37777',1,1654587002,1653526698,0,'<Item>\r\n<DeviceID>34020000001310000002</DeviceID>\r\n<Name>IP:192.168.1.177 -球机</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.177</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>1</PTZType>\r\n</Info>\r\n</Item>'),(3,'34020000001310000003','44010200492000000120',0,'112dahua1楼','Dahua','DH-NVR504-I','00000000080000000008','','','','1','0.0','0.0','192.168.1.112','37777',1,1654587002,1653526698,0,'<Item>\r\n<DeviceID>34020000001310000003</DeviceID>\r\n<Name>112dahua1楼</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.112</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>1</PTZType>\r\n</Info>\r\n</Item>'),(4,'34020000001310000004','44010200492000000120',0,'IP:192.168.1.158-枪机','Dahua','DH-NVR504-I','00000000080000000008','','','','3','0.0','0.0','192.168.1.158','37777',1,1654587002,1653526698,0,'<Item>\r\n<DeviceID>34020000001310000004</DeviceID>\r\n<Name>IP:192.168.1.158-枪机</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.158</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>'),(5,'34020000001310000005','44010200492000000120',0,'路灯杆-球型','Dahua','DH-NVR504-I','00000000080000000008','','','','1','0.0','0.0','192.168.1.144','37777',1,1654587002,1653526698,0,'<Item>\r\n<DeviceID>34020000001310000005</DeviceID>\r\n<Name>路灯杆-球型</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.144</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>1</PTZType>\r\n</Info>\r\n</Item>'),(6,'34020000001310000006','44010200492000000120',0,'IP:192.168.1.148-球机2','Dahua','DH-NVR504-I','00000000080000000008','','','','1','0.0','0.0','192.168.1.148','37777',1,1654587002,1653526698,0,'<Item>\r\n<DeviceID>34020000001310000006</DeviceID>\r\n<Name>IP:192.168.1.148-球机2</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.148</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>1</PTZType>\r\n</Info>\r\n</Item>'),(7,'34020000001310000007','44010200492000000120',0,'通道一','Dahua','DH-NVR504-I','00000000080000000008','','','','3','0.0','0.0','192.168.1.198','37777',1,1654587002,1653526698,0,'<Item>\r\n<DeviceID>34020000001310000007</DeviceID>\r\n<Name>通道一</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.198</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>'),(8,'00000000080000000008','44010200492000000120',1,'abddd','wvp-pro','live','','','','','0','0.0','0.0','null','0',1,1654587002,1653526827,0,'<Item>\r\n<DeviceID>00000000080000000008</DeviceID>\r\n<Name>abddd</Name>\r\n<Manufacturer>wvp-pro</Manufacturer>\r\n<Model>live</Model>\r\n<Owner>wvp-pro</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>null</Address>\r\n<Parental>1</Parental>\r\n<ParentID>44010200492000000120</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>null</IPAddress>\r\n<Port>0</Port>\r\n<Info>\r\n<PTZType>0</PTZType>\r\n</Info>\r\n</Item>'),(9,'34020000001310000114','44010200492000000120',0,'澶у??2妤艰蛋寤?','Dahua','IPC-HDW1235C-A','00000000080000000008','','','','0','0.0','0.0','axy','0',1,1654138509,1653526827,0,'<Item>\r\n<DeviceID>34020000001310000114</DeviceID>\r\n<Name>澶у??2妤艰蛋寤?</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>IPC-HDW1235C-A</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress></IPAddress>\r\n<Port>0</Port>\r\n<Info>\r\n<PTZType>0</PTZType>\r\n</Info>\r\n</Item>'),(10,'34020000001310000124','44010200492000000120',0,'IPC','Dahua','IPC-HFW4243F-ZYL-AS','00000000080000000008','','','','3','0.0','0.0','axy','0',1,1654138509,1653526828,0,'<Item>\r\n<DeviceID>34020000001310000124</DeviceID>\r\n<Name>IPC</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>IPC-HFW4243F-ZYL-AS</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress></IPAddress>\r\n<Port>0</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>'),(11,'34020000001310000127','44010200492000000120',0,'四楼办公室','Dahua','IPC-HDBW4433R-ZS','00000000080000000008','','','','3','0.0','0.0','axy','0',1,1654138509,1653526828,0,'<Item>\r\n<DeviceID>34020000001310000127</DeviceID>\r\n<Name>四楼办公室</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>IPC-HDBW4433R-ZS</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress></IPAddress>\r\n<Port>0</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>'),(12,'34020000001310000141','44010200492000000120',0,'球机141','Dahua','DH-SD6C84FX-GNP(ZJ)-A','00000000080000000008','','','','3','0.0','0.0','axy','0',1,1654138509,1653526828,0,'<Item>\r\n<DeviceID>34020000001310000141</DeviceID>\r\n<Name>球机141</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-SD6C84FX-GNP(ZJ)-A</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress></IPAddress>\r\n<Port>0</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>'),(13,'34020000001310000151','44010200492000000120',0,'大门口','Dahua','IPC-HFW2433F-ZAS','00000000080000000008','','','','3','0.0','0.0','axy','0',1,1654138509,1654054367,0,'<Item>\r\n<DeviceID>34020000001310000151</DeviceID>\r\n<Name>大门口</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>IPC-HFW2433F-ZAS</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress></IPAddress>\r\n<Port>0</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>'),(14,'34020000001310000008','44010200492000000120',0,'4楼茶水间','Dahua','DH-NVR504-I','00000000080000000008','','','','3','0.0','0.0','192.168.1.64','37777',0,1654587003,1654582919,0,'<Item>\r\n<DeviceID>34020000001310000008</DeviceID>\r\n<Name>4楼茶水间</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>OFF</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.64</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>'),(15,'34020000001310000009','44010200492000000120',0,'dahua4楼办公室门口','Dahua','DH-NVR504-I','00000000080000000008','','','','3','0.0','0.0','192.168.1.111','37777',1,1654587003,1654582919,0,'<Item>\r\n<DeviceID>34020000001310000009</DeviceID>\r\n<Name>dahua4楼办公室门口</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.111</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>'),(16,'34020000001310000010','44010200492000000120',0,'JYIPC','Dahua','DH-NVR504-I','00000000080000000008','','','','3','0.0','0.0','192.168.1.217','37777',1,1654587003,1654582919,0,'<Item>\r\n<DeviceID>34020000001310000010</DeviceID>\r\n<Name>JYIPC</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>ON</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.217</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>'),(17,'34020000001310000011','44010200492000000120',0,'190','Dahua','DH-NVR504-I','00000000080000000008','','','','3','0.0','0.0','192.168.1.65','37777',0,1654587003,1654582919,0,'<Item>\r\n<DeviceID>34020000001310000011</DeviceID>\r\n<Name>190</Name>\r\n<Manufacturer>Dahua</Manufacturer>\r\n<Model>DH-NVR504-I</Model>\r\n<Owner>0</Owner>\r\n<CivilCode>440102</CivilCode>\r\n<Address>axy</Address>\r\n<Parental>0</Parental>\r\n<ParentID>00000000080000000008</ParentID>\r\n<Secrecy>0</Secrecy>\r\n<RegisterWay>1</RegisterWay>\r\n<Status>OFF</Status>\r\n<Longitude>0.0</Longitude>\r\n<Latitude>0.0</Latitude>\r\n<IPAddress>192.168.1.65</IPAddress>\r\n<Port>37777</Port>\r\n<Info>\r\n<PTZType>3</PTZType>\r\n</Info>\r\n</Item>');
/*!40000 ALTER TABLE `device_node_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_cache`
--

DROP TABLE IF EXISTS `django_cache`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_cache` (
  `cache_key` varchar(255) NOT NULL,
  `value` longtext NOT NULL,
  `expires` datetime(6) NOT NULL,
  PRIMARY KEY (`cache_key`),
  KEY `django_cache_expires` (`expires`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_cache`
--

LOCK TABLES `django_cache` WRITE;
/*!40000 ALTER TABLE `django_cache` DISABLE KEYS */;
INSERT INTO `django_cache` VALUES ('fds','111','2022-04-21 09:02:11.000000'),('s','ddfd1','2022-04-20 09:30:11.000000');
/*!40000 ALTER TABLE `django_cache` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (1,'admin','logentry'),(3,'auth','group'),(2,'auth','permission'),(4,'auth','user'),(5,'contenttypes','contenttype'),(9,'gbs_zxiat','channelinfo'),(10,'gbs_zxiat','channelsnapshot'),(14,'gbs_zxiat','decoderalgoinfo'),(15,'gbs_zxiat','decoderchannelalgoconf'),(13,'gbs_zxiat','decodersceneinfo'),(12,'gbs_zxiat','kvsettinginfo'),(8,'gbs_zxiat','platforminfo'),(7,'gbs_zxiat','serviceinfo'),(11,'gbs_zxiat','sharedinfo'),(6,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2022-04-15 10:57:53.600648'),(2,'auth','0001_initial','2022-04-15 10:57:55.519817'),(3,'admin','0001_initial','2022-04-15 10:58:03.818067'),(4,'admin','0002_logentry_remove_auto_add','2022-04-15 10:58:06.038108'),(5,'admin','0003_logentry_add_action_flag_choices','2022-04-15 10:58:06.203421'),(6,'contenttypes','0002_remove_content_type_name','2022-04-15 10:58:07.856956'),(7,'auth','0002_alter_permission_name_max_length','2022-04-15 10:58:09.316347'),(8,'auth','0003_alter_user_email_max_length','2022-04-15 10:58:10.562959'),(9,'auth','0004_alter_user_username_opts','2022-04-15 10:58:10.799154'),(10,'auth','0005_alter_user_last_login_null','2022-04-15 10:58:11.978745'),(11,'auth','0006_require_contenttypes_0002','2022-04-15 10:58:12.122543'),(12,'auth','0007_alter_validators_add_error_messages','2022-04-15 10:58:12.232394'),(13,'auth','0008_alter_user_username_max_length','2022-04-15 10:58:13.714407'),(14,'auth','0009_alter_user_last_name_max_length','2022-04-15 10:58:14.932589'),(15,'auth','0010_alter_group_name_max_length','2022-04-15 10:58:16.131598'),(16,'auth','0011_update_proxy_permissions','2022-04-15 10:58:16.291988'),(17,'sessions','0001_initial','2022-04-15 10:58:16.754145'),(18,'gbs_zxiat','0001_initial','2022-04-15 10:59:19.959971');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('16miz8k1a4og9d1uvof1419ylmen3lxg','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:44:44.017244'),('1vcbw339s7z48bvbknm204wj749k1r4u','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 14:32:17.354666'),('2jhtx1h5jnyvvw2m9kzfdgeg5cc4selh','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-29 17:25:15.807524'),('3dyca6s4y6gvmwmja889vxdg2q548qde','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:43:33.768514'),('4czi8iwns6h48xqucpiwu1to41go31xo','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-06-07 15:43:43.212773'),('75jzbedrp0etj8yafrmirke3dj6q8ewp','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-06-07 16:40:34.613121'),('7r849byucpj2i76yioiw076q8y2xgn1c','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-30 15:04:43.534734'),('7xxet7zjp3xwemikbsaq51myhzaitwpu','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-29 17:25:09.379426'),('bvqq2fe6rx7i8ngoedjn4zqe7iwhle3q','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:43:58.310520'),('f68985150264b5c766770180a0be7624','MjVhMzU5N2MzMzMxMGMzMDk1ZTg0ZWYzOWRjMWM0ODY0YmJjMjZlNzp7InRlc3QiOjIzLCJ1c2VyX2lkIjoxfQ==','2041-07-25 15:17:13.090637'),('fvoy92k85gjkc8tweq3vz1abmwxofbir','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-29 17:58:07.033317'),('grr7kqiqzgmtzs7xpf4ovvvtez4gy2sy','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-06-20 15:55:34.858705'),('ihm1y9b3py8levhhpa0tv4oxtbu13p84','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:46:41.687528'),('o38t23a46cda5yu2liqzxn5zydffa80h','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:43:51.175924'),('ojurpukyqie7ax15pu4e427vqkmj0cw2','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-29 17:50:56.198600'),('pqjq9vmd3tm174e8ev900erf99gthl1i','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 15:20:14.180445'),('q8k0g7xj2bpj2kotnqqz4y3dfod8m8g5','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:44:27.634299'),('ryeruyaz620dm8utpf77jaikx13geuh9','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:46:38.938192'),('s2hbzy1u2r4o1v824eun76i5lztmz8bo','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:45:07.842063'),('t2j3thpjoeqi9n59e5n3axzwyr935kkj','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-16 09:41:44.146157'),('ut3rdvsll2lwoqva69v2zbfv415bumwv','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:43:55.092532'),('vidbwf8sg7xj27t9dfen8zk936b69048','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-25 15:47:15.930756'),('vx35hd24rzjw75ljf7qhyq62kofl1ssy','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-29 17:32:14.927951'),('xi26tet26j5g3qlw5nqzn9bbqo9p5d72','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 15:16:18.894344'),('ydx0rfua45sh3lso5j09ocj78emavqp0','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-06-20 14:48:34.787838'),('ye9b0tdtxawr4bclkwlhm868ib7kyu7d','YTZjMzM3MmI5Y2U2MGJiYThkMmQxMDY2YjdmNGI1NjJmM2ZjMDVmMjp7Il9hdXRoX3VzZXJfaWQiOiIxIiwiX2F1dGhfdXNlcl9iYWNrZW5kIjoiZGphbmdvLmNvbnRyaWIuYXV0aC5iYWNrZW5kcy5Nb2RlbEJhY2tlbmQiLCJfYXV0aF91c2VyX2hhc2giOiJhNzU0M2Q5OWRkMDMwN2ZmZWMyNmI5YjBmMjVjZWZlNGQ2ZWMzZjY5In0=','2041-07-15 17:46:19.156558');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gateway_info`
--

DROP TABLE IF EXISTS `gateway_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gateway_info` (
  `pk` int unsigned NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL DEFAULT '',
  `code` varchar(32) NOT NULL DEFAULT '',
  `ip` varchar(15) NOT NULL DEFAULT '',
  `port` int unsigned NOT NULL DEFAULT '0',
  `is_wandev` int unsigned NOT NULL DEFAULT '0',
  `manufacture` varchar(100) NOT NULL DEFAULT '',
  `rtp_mode` int unsigned NOT NULL DEFAULT '0',
  `addtime` int unsigned NOT NULL DEFAULT '0',
  `last_msg_time` int unsigned NOT NULL DEFAULT '0',
  `heartbeat_time` int unsigned NOT NULL DEFAULT '0',
  `reg_time` int unsigned NOT NULL DEFAULT '0',
  `dir_code_id` varchar(50) NOT NULL DEFAULT '',
  `last_scan_catalog_time` int unsigned NOT NULL DEFAULT '0',
  `limit_ipport` int unsigned NOT NULL DEFAULT '0',
  `model` varchar(250) NOT NULL DEFAULT '',
  PRIMARY KEY (`pk`),
  UNIQUE KEY `name` (`name`),
  UNIQUE KEY `gateway_info_code_uindex` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb3 COMMENT='平台信息(就是下级平台)';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gateway_info`
--

LOCK TABLES `gateway_info` WRITE;
/*!40000 ALTER TABLE `gateway_info` DISABLE KEYS */;
INSERT INTO `gateway_info` VALUES (1,'123111222','11111111110000000009','1.1.1.1',3307,0,'',1,1653379397,0,0,0,'11111111110000000000',0,0,''),(3,'217-cam','34020000001320000217','192.168.1.217',5060,0,'JCO',1,1653449009,1654587123,1654587123,1654131823,'11111111110000000000',1654583295,1,'V1700N-N'),(4,'wvp','44010200492000000120','192.168.1.120',5060,0,'wvp',0,1653472634,1654587123,1654587123,1653525705,'11111111110000000000',1654586846,0,'wvp-28181-2.0');
/*!40000 ALTER TABLE `gateway_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `service_info`
--

DROP TABLE IF EXISTS `service_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `service_info` (
  `service_id` int NOT NULL AUTO_INCREMENT,
  `type` int unsigned NOT NULL DEFAULT '0',
  `ip` varchar(15) NOT NULL,
  `port` int unsigned NOT NULL DEFAULT '0',
  `addtime` int unsigned NOT NULL DEFAULT '0',
  `status` int unsigned NOT NULL DEFAULT '0',
  `status_uptime` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`service_id`),
  UNIQUE KEY `service_info_type_ip_port_275e01f1_uniq` (`type`,`ip`,`port`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COMMENT='服务管理';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `service_info`
--

LOCK TABLES `service_info` WRITE;
/*!40000 ALTER TABLE `service_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `service_info` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `shared_info`
--

DROP TABLE IF EXISTS `shared_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `shared_info` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(120) NOT NULL,
  `parent_sip_ip` varchar(20) NOT NULL,
  `parent_sip_port` int unsigned NOT NULL DEFAULT '0',
  `my_gb_code` varchar(30) NOT NULL DEFAULT '',
  `share_node_info` longtext NOT NULL,
  `reg_duration` int unsigned NOT NULL DEFAULT '0',
  `heart_duration` int unsigned NOT NULL DEFAULT '0',
  `expire_times` int unsigned NOT NULL DEFAULT '0',
  `addtime` int unsigned NOT NULL DEFAULT '0',
  `update_time` int unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `shared_info`
--

LOCK TABLES `shared_info` WRITE;
/*!40000 ALTER TABLE `shared_info` DISABLE KEYS */;
/*!40000 ALTER TABLE `shared_info` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-06-07 15:32:09
