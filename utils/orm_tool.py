# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/5/6
# orm 工具模块。可以方便的调用django中的orm功能

import sys
import os



def init_orm():
    MY_PATH = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.join(MY_PATH, ".."))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gbs_zxiat.settings")
    import django
    django.setup()
    from gbs_zxiat import models
    return models



if __name__ == '__main__':
    models = init_orm()
    models.CustomSubDir.objects.all()