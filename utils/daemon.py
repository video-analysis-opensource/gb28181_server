# coding:utf-8
# __author__ = "zhou"
# create by zhou on 2020/8/28
from __future__ import absolute_import, division, print_function, \
    with_statement
import os
import sys
import logging
import signal
import time

# this module is ported from ShadowVPN daemon.c


def redirect_output(output="/dev/null"):
    out = open(output, "ba+")
    devnull_fd = os.open(os.devnull, os.O_RDWR)
    os.dup2(devnull_fd, sys.stdin.fileno())
    os.dup2(out.fileno(), sys.stdout.fileno())
    os.dup2(out.fileno(), sys.stderr.fileno())
    out.close()
    os.close(devnull_fd)

def daemon_start():

    def handle_exit(signum, _):
        if signum == signal.SIGTERM:
            sys.exit(0)
        sys.exit(1)

    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    # fork only once because we are sure parent will exit
    pid = os.fork()
    assert pid != -1

    if pid > 0:
        # parent waits for its child
        time.sleep(5)
        sys.exit(0)

    # child signals its parent to exit
    ppid = os.getppid()
    pid = os.getpid()
    os.setsid()
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    os.kill(ppid, signal.SIGTERM)
    try:
        sys.stdin.close()
    except:
        pass
    return pid


def set_user(username):
    if username is None:
        return

    import pwd
    import grp

    try:
        pwrec = pwd.getpwnam(username)
    except KeyError:
        logging.error('user not found: %s' % username)
        raise
    user = pwrec[0]
    uid = pwrec[2]
    gid = pwrec[3]

    cur_uid = os.getuid()
    if uid == cur_uid:
        return
    if cur_uid != 0:
        logging.error('can not set user as nonroot user')
        # will raise later

    # inspired by supervisor
    if hasattr(os, 'setgroups'):
        groups = [grprec[2] for grprec in grp.getgrall() if user in grprec[3]]
        groups.insert(0, gid)
        os.setgroups(groups)
    os.setgid(gid)
    os.setuid(uid)

if __name__ == '__main__':
    daemon_start()
    while 1:
        time.sleep(1)
