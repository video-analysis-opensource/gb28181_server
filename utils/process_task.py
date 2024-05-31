# coding:utf-8
__author__ = "zhou"
# create by zhou on 2020/8/28
import hashlib
import cloudpickle
import os
import time
import random
import string
import json
import sys
import base64
import datetime



_current_dir = os.path.abspath(os.path.dirname(__file__))
_my_path = os.path.join(_current_dir, 'process_task.py')
if sys.executable.endswith('python') or sys.executable.endswith('python3') or 'python' in sys.executable:
    _py_path = sys.executable
elif sys.executable.endswith('uwsgi') or sys.executable.endswith('uwsgi3'):
    if sys.version_info.major == 2:
        _py_path = os.path.join(os.path.dirname(sys.executable), 'python2')
        if not  os.path.exists(_py_path):
            _py_path = 'python2'
    else:
        _py_path = os.path.join(os.path.dirname(sys.executable), 'python3')
        if not os.path.exists(_py_path):
            _py_path = 'python3'
else:
    _py_path = 'python%s' % sys.version_info.major


def run_task(fun, args=(), kwargs={}):
    def _gen(length: int = 8):
        "生成随机字符串"
        _ = random.sample(string.ascii_letters[:26] + "0123456789", length)
        return "".join(_)
    task_id = _gen(10)
    fun = cloudpickle.dumps(fun)
    fun_b64 = base64.b64encode(fun).decode()
    data = {"fun_b64":fun_b64, 'args': args, 'kwargs': kwargs}
    # print(data)
    data_json = json.dumps(data)
    os.system("mkdir -p /tmp/process_task")
    os.system("mkdir -p /tmp/process_task_log")
    os.system("mkdir -p /tmp/process_task_result")

    # 对于过老的log删除掉
    for i in  os.listdir('/tmp/process_task_log'):
        if i.endswith(".log"):
            _real_path = os.path.join('/tmp/process_task_log', i)
            try:
                modify_time = os.path.getmtime(_real_path)
                if time.time() - modify_time >= 86400*2:
                    os.system("rm -rf %s" % _real_path)
            except:
                pass

    # 对于过老的result删除掉
    for i in  os.listdir('/tmp/process_task_result'):
        if i.endswith(".log"):
            _real_path = os.path.join('/tmp/process_task_result', i)
            try:
                modify_time = os.path.getmtime(_real_path)
                if time.time() - modify_time >= 86400*2:
                    os.system("rm -rf %s" % _real_path)
            except:
                pass


    with open("/tmp/process_task/%s" % task_id, "w") as f:
        f.write(data_json)

    os.system("%s %s/process_task.py %s " %
              (_py_path, _current_dir, task_id))
    return task_id




if __name__ == '__main__':
    import daemon,os
    task_id = sys.argv[-1]
    os.task_id = task_id
    os.system("mkdir -p /tmp/process_task/pids")
    with open("/tmp/process_task/%s" % task_id, "r") as f:
        data_json = f.read()
    os.system("rm -rf /tmp/process_task/%s" % task_id)
    data = json.loads(data_json)
    fun = cloudpickle.loads(base64.b64decode(data['fun_b64'].encode()))
    args = data['args']
    kwargs = data['kwargs']
    # print(args,kwargs)
    daemon.daemon_start()
    with open(f"/tmp/process_task/pids/{task_id}", "w") as f:
        f.write(str(os.getpid()))
    #import setproctitle
    #setproctitle.setproctitle(f"httpflv_decoder_{task_id}",)
    result = fun(*args, **kwargs)
    result_json = json.dumps(result)
    os.system("mkdir -p /tmp/process_task_result")
    with open("/tmp/process_task_result/%s" % task_id, "w") as f:
        f.write(result_json)