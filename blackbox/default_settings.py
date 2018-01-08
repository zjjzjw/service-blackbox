# -*- coding: utf-8 -*-

#
# basic
#
DEBUG = True
DAEMON = False

#
# log
#
MASTER_LOG = '/tmp/blackbox-master.log'
WORKER_LOG = '/tmp/blackbox-worker.log'
LOG_FORMAT = '[%(asctime)s %(levelname)s(%(process)d)] %(message)s'

#
# sockets definition
#
CLIENT_SOCK    = "tcp://*:7555"
RELOAD_SOCK    = "tcp://*:7556"
WORKER_SOCK    = "ipc:///tmp/blackbox-worker.ipc"
HEARTBEAT_SOCK = "ipc:///tmp/blackbox-heartbeat.ipc"
LOG_SOCK       = "tcp://*:7557"

#
# shared files
#
MASTER_PID = '/tmp/blackbox-master.pid'
MASTER_STATUS_SOCK = '/tmp/blackbox-master.sock'

#
# database
#
DB_USER   = "aifang"
DB_PASSWD = "123456"
DB_HOST   = "192.168.1.167"
DB_DBNAME = "aifang_dw"

#
# python executable for worker
#
import blackbox
from os.path import abspath
_ = abspath('{}/../.virtualenv/bin'.format(blackbox.__path__[0]))
PYTHON_EXECUTABLE = "{}/python".format(_)

#
# main loop
#
INTERVAL           = 5000
HEARTBEAT_INTERVAL = 2000    #worker
POLLER_INTERVAL    = 1000    #worker
STANDARD           = 0.95     #95% execution time

#
# kite-line
#
KL_RPC_ENDPOINT = 'tcp://192.168.1.62:11234'
BLACKBOX_RPC_ENDPOINT = 'tcp://127.0.0.1:7555'
LOG_RPC_ENDPOINT ='tcp://127.0.0.1:7557'
KL_SP_ID = 'blackbox'
