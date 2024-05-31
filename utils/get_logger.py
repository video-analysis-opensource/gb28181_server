# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/5/26
import logging
from logging import handlers,Formatter
import multiprocessing


def get_logger(log_name, backupCount=7, *args, **kwargs):
    """
    init logger
    :param log_name:
    :param backupCount:
    :param args:
    :param kwargs:
    :return:
    """
    #if not multi:
    logger = logging.getLogger()
    handler = handlers.TimedRotatingFileHandler(log_name, when='D', interval=1,
                                                backupCount=backupCount)
    formatter = Formatter('[%(asctime)s: %(levelname)s]: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger