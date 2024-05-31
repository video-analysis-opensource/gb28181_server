# coding:utf-8
__author__ = "zkp"
# create by zkp on 2022/5/13


def green_print(*msg):
    for _ in msg:
        print('\033[92m%s \033[0m' % _)
    print('')


def red_print(*msg):
    for _ in msg:
        print('\033[91m%s \033[0m' % _)
    print('')


def yellow_print(*msg):
    for _ in msg:
        print('\033[93m%s \033[0m' % _)
    print('')