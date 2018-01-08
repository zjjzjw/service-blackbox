# -*- coding: utf-8 -*-
from __future__ import print_function
import errno
import logging
import os
from signal import SIGHUP, SIGQUIT, SIGUSR1
from socket import AF_UNIX, SOCK_STREAM, socket
import sys

from blackbox.master import Master


usage = """
usage:

    bbctl reload|start|status|stop
"""

def kill(pid, signal):
    try:
        os.kill(pid, signal)
    except OSError as e:
        if e.errno == errno.ESRCH:
            print('process not found, maybe dead?')
        elif e.errno in (errno.EACCES, errno.EPERM):
            print('permission denied, maybe difference user?')

def read_pid_file(pidfile):
    """None if pid file does not exists"""
    if os.path.isfile(pidfile):
        with open(pidfile) as f:
            pid = int(f.read().strip())
    else:
        pid = None
    return pid

def main():
    if len(sys.argv) == 1:
        print(usage)
        return

    bb = Master(__name__)
    pidfile = bb.config['MASTER_PID']
    pid = read_pid_file(pidfile)
    if sys.argv[1] == 'start':
        if pid:
            print('blackbox already started?')
        else:
            bb.start().join()
    elif sys.argv[1] == 'status':
        if pid:
            kill(pid, SIGUSR1)
            sock = socket(AF_UNIX, SOCK_STREAM)
            sock.connect(bb.config['MASTER_STATUS_SOCK'])
            status = sock.recv(1024)
            print(status)
        else:
            print('blackbox not started?')
    elif sys.argv[1] == 'stop':
        if pid:
            kill(pid, SIGQUIT)
        else:
            print('blackbox not started?')
    elif sys.argv[1] == 'reload':
        if pid:
            kill(pid, SIGHUP)
        else:
            print('blackbox not started?')
    else:
        print('unknown command: {}'.format(sys.argv[1]))
        print(usage)
