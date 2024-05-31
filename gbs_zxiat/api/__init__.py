# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/4/15
import os

_ = os.listdir(os.path.dirname(__file__))
# 导入所有.py文件
for i in _:
    if i .endswith(".py") and not "__" in i:
        # print("__import__", i)
        # __import__(i)
        # importlib.import_module(i.replace(".py",""))
        exec("from . import %s" % i.replace(".py",""))