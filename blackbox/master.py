# -*- coding: utf-8 -*-
import atexit
import errno
import json
from logging import INFO
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler
import os
from signal import SIGHUP, SIGINT, SIGQUIT, SIGTERM, SIGUSR1, signal
import socket
import subprocess
import time

from aps.client import APS
from aps.base import wait_for_replies
from msgpack import packb, unpackb
import mysql.connector
import zmq

from blackbox import BaseApplication
from blackbox.util.helpers import millitime
import sys


VERSION = r'V1'
EMPTY = r''


class Master(BaseApplication):

    QUEUE_SIGS = [SIGQUIT, SIGINT, SIGTERM, SIGUSR1, SIGHUP]

    EXIT_SIGS = [SIGQUIT, SIGINT, SIGTERM]

    SIG_QUEUE = []

    def __init__(self, import_name):

        super(Master, self).__init__(import_name)

        self.load_config()

        self.last_check = millitime()
        self.pid = os.getpid()

        #
        # controllers data structure
        # self.controllers =>
        # {
        #   "ctlr_name1" => [<page_id>, <target>, <timestamp>],
        #   "ctlr_name2" => [<page_id>, <target>, <timestamp>],
        # }
        #
        self.controllers = {}
        self.workers = {} # Popen object lists
        self.requests = 0
        self.maintain_cnt = 1
        self.quit = False

        if not self.debug:
            formatter = Formatter(self.config['LOG_FORMAT'])
            handler = TimedRotatingFileHandler(self.config['MASTER_LOG'],
                                               when='midnight')
            handler.setLevel(INFO)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def initialize_status_socket(self):
        """get status info in memory through socket"""
        if os.path.isfile(self.config['MASTER_STATUS_SOCK']):
            self.quit()

        self.status_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.status_socket.bind(self.config['MASTER_STATUS_SOCK'])
        self.status_socket.listen(1)

    def load_config(self):
        """load config"""
        from blackbox import default_settings
        self.config.from_object(default_settings)
        config_file = os.environ.get('BLACKBOX_CONFIG')
        if config_file:
            config_file = os.path.abspath(config_file)
            if os.path.isfile(config_file):
                self.config.from_pyfile(config_file)

    def kl_register(self):
        """send sp.up request to kiteline"""
        kl_ep = self.config['KL_RPC_ENDPOINT']
        kl = APS()
        kl.connect(kl_ep)

        sp_id = self.config['KL_SP_ID']
        ep = self.config['BLACKBOX_RPC_ENDPOINT']
        version = VERSION
        hdl = kl.start_request('sp.up', [sp_id, ep, version])

        replies = wait_for_replies(timeout=2000)
        response = replies.get(hdl)

        if response is None:
            self.logger.warn('kitelined cannot be reached')
        elif response.status != 200:
            self.logger.warn('kitelined response error when registering')

    def kl_unregister(self):
        """send sp.down request to kiteline"""
        kl_ep = self.config['KL_RPC_ENDPOINT']
        kl = APS()
        kl.connect(kl_ep)

        ep = self.config['BLACKBOX_RPC_ENDPOINT']
        hdl = kl.start_request('sp.down', [ep])

        replies = wait_for_replies(timeout=2000)
        response = replies.get(hdl)

        if response is None:
            self.logger.warn('kitelined cannot be reached')
        elif response.status != 200:
            self.logger.warn('kitelined response error when unregistering')

    def daemonize(self):
        # TODO: magic unix 2 forks
        raise NotImplementedError()

    def handle_signal(self, sig):
        if sig == SIGHUP:
            # TODO: reload config, cleanup old pid, socks, sockets ?
            self.reload_controllers()
            print("SIGUP")

        elif sig in self.EXIT_SIGS:
            # SIGINT quit
            # FIXME: soft quit
            for ctlr in self.controllers.keys():
                self.murder_worker(self.workers[ctlr])

            self.quit = True

        elif sig == SIGUSR1:
            # SIGUSR1 get status

            conn, addr = self.status_socket.accept()
            data = "\n\n===== blackbox master =====\n"
            data += "Version: {}\nPID: {}\nNow have {} worker(s)\n\n".\
                   format(VERSION, self.pid, len(self.controllers))
            for c in self.controllers.keys():
                data += "  PID: {} => {}\n".format(self.workers[c].pid, c)
            data += "\n\nToday have handled {} requests".format(self.requests)
            data += "\n===========================\n\n"
            conn.send(data)

        else:
            self.logger.info("[Warnings]Signal handle innormally!")
            assert False

    def start(self):
        """prepare to start. return self in order to run join"""

        def _handle(sig, frames):
            self.SIG_QUEUE.append(sig)

        for sig in self.QUEUE_SIGS:
            signal(sig, _handle)
        
        self.initialize_status_socket()

        def create_socket(socket_type, endpoint):
            socket = zmq.Socket(zmq.Context.instance(), socket_type)
            socket.setsockopt(zmq.LINGER, 0)
            socket.bind(endpoint)
            return socket

        self.client_sock = create_socket(zmq.PULL, self.config['CLIENT_SOCK'])
        self.reload_sock = create_socket(zmq.PULL, self.config['RELOAD_SOCK'])
        self.worker_sock = create_socket(zmq.PUB, self.config['WORKER_SOCK'])
        self.heartbeat_sock = create_socket(zmq.PULL,
                                              self.config['HEARTBEAT_SOCK'])
        
        ctx = zmq.Context()
        self.log_sock = zmq.Socket(ctx, zmq.PUSH)
        self.log_sock.connect(self.config['LOG_RPC_ENDPOINT'])

        atexit.register(self.clean_socks)

        if self.config['DAEMON']:
            self.daemonize()

        poller = zmq.Poller()
        poller.register(self.client_sock, zmq.POLLIN)
        poller.register(self.heartbeat_sock, zmq.POLLIN)
        poller.register(self.reload_sock, zmq.POLLIN)

        self.poller = poller

        with open(self.config['MASTER_PID'], 'w') as pidfile:
            pidfile.write('{}'.format(self.pid))

        self.controllers = self.get_controllers()
        self.spawn_missing_workers()

        return self

    def join(self):
        """main loop"""

        self.kl_register()

        while self.quit == False:
            self.reap_workers()
            if len(self.SIG_QUEUE) > 0:
                print("------------------------------------------");
                sig = self.SIG_QUEUE.pop(0)
                self.handle_signal(sig)
            else:
                self.maintain()

                try:
                    events = self.poller.poll(self.config['INTERVAL'])
                except zmq.ZMQError as e:
                    if e.errno == errno.EINTR:
                        continue
                    else:
                        pass

                for socket, flags in events:

                    self.requests += 1

                    try:
                        if socket == self.client_sock:
                            self.handle_client()
                        elif socket == self.heartbeat_sock:
                            self.handle_heartbeat()
                        elif socket == self.reload_sock:
                            self.handle_reload()
                        else:
                            assert False
                    except:
                        self.logger.exception('Error when handling events')

    def reset_request_num(self):
        hour = time.strftime('%H', time.localtime(time.time()))
        miniute = time.strftime('%M', time.localtime(time.time()))
        miniutes = ['00', '01', '02', '03']
        if str(hour) == '00' and str(miniute) in miniutes:
            self.requests = 0

    def spawn_missing_workers(self):
        """spawn missing workers from self.controllers"""
        for c in self.controllers:
            if c not in self.workers:
                self.logger.info('spawn missing worker: {}'.format(c))
                self.create_worker(c)

    def reap_workers(self):
        """reap all workers"""
        need_delete = []
        for c in self.workers:
            worker = self.workers[c]
            _ = worker.poll()
            if _ is not None:
                need_delete.append(c)

        for c in need_delete:
            del self.workers[c]


    def maintain(self):
        now = millitime()
        if now - self.last_check < self.config['INTERVAL']:
            return
        self.logger.info("maintain workers")
        self.maintain_cnt = self.maintain_cnt + 1
        if self.maintain_cnt > 720:
            # murder all workders after an hour
            self.maintain_cnt = 1
            for c in self.controllers:
                if c in self.workers:
                    self.murder_worker(self.workers[c])
        self.last_check = self.last_check + self.config['INTERVAL']

        ## FIXME: if heartbeat time is not updated, does that mean the
        ## worker process should be killed first ? then create once again.

        # for c in self.controllers:
        #     t = self.controllers[c][3]
        #     if self.last_check - t > self.config['INTERVAL']:
        #         self.create_worker(c)

        self.spawn_missing_workers()

    def create_worker(self, name):
        """create worker, arg consist of

        page_id,
        controller_name,
        target

        joined by hyphen, such as

        `1-SampleController-200`
        """
        self.logger.info("creating worker {}".format(name))
        controller = self.controllers[name]
        page_id, target, domain, _ = controller
        arg = "{}-{}-{}-{}".format(page_id, domain ,name, target)
        cmd_frags = [self.config['PYTHON_EXECUTABLE'], '-m', 'blackbox.worker',
                     '-c', arg]
        self.logger.info('cmd: {}'.format(" ".join(cmd_frags)))
        p = subprocess.Popen(cmd_frags)
        self.workers[name] = p

    def murder_worker(self, process):
        """murder a worker via send QUIT signal to worker process"""
        try:
            os.kill(process.pid, SIGQUIT)
        except OSError as e:
            if e.errno == errno.ESRCH:
                self.logger.warn('worker pid: {} not found'.format(process.pid))
            elif e.errno in (errno.EPERM, errno.EACCES):
                self.logger.warn('cannot kill worker pid: {}, '
                                 'permission denied'.format(process.pid))

    def update_heartbeat(self, frames):
        """update worker heartbeat last check timestamp"""
        i = frames.index(EMPTY)
        name = unpackb(frames[i+1])
        if name in self.controllers:
            now = millitime()
            self.controllers[name][3] = now

    def handle_heartbeat(self):
        while True:
            try:
                frames = self.heartbeat_sock.recv_multipart(zmq.NOBLOCK)
            except zmq.ZMQError as e:
                if e.errno == errno.EAGAIN:
                    break
                else:
                    pass
            self.update_heartbeat(frames)

    def build_pub_frames(self, frames):
        i = frames.index(EMPTY)
        try:
            json_data = unpackb(frames[i+1])
        except:
            self.logger.exception('Format Error: ' + str(frames))
            raise
        else:
            data = json.loads(json_data)
            print(data)
            name = data['controller_name']
            domain = data['site']
            if name in self.controllers:
                page_id = self.controllers[name][0]
            else:
                page_id = 0
            frames.insert(0, str(page_id) + "-" + str(domain) + "-" + str(name))
            return frames

    def publish(self, frames):
        self.log_sock.send_multipart(frames)
        send_frames = self.build_pub_frames(frames)
        self.worker_sock.send_multipart(send_frames)

    def handle_client(self):
        while True:
            try:
                frames = self.client_sock.recv_multipart(zmq.NOBLOCK)
            except zmq.ZMQError as e:
                if e.errno == errno.EAGAIN:
                    break
                else:
                    pass
            self.publish(frames)

    def handle_reload(self):
        """handle reloading message"""
        try:
            frames = self.reload_sock.recv_multipart(zmq.NOBLOCK)
        except:
            pass

        i = frames.index(EMPTY)

        if frames[i - 2] == '\x04':
            self.reload_controllers()

    def reload_controllers(self):
        """reload controllers setting from database"""
        #reload controllers
        new_controllers = self.get_controllers()

        #remove old worker
        for c in self.controllers:
            if c not in new_controllers:
                self.logger.info('remove obsolete worker: {}'.format(c))
                self.murder_worker(self.workers[c])

        self.controllers = new_controllers
        self.logger.info('controllers reloaded.')

    def get_controllers(self):

        # FIXME: use SQLALchemy for database accessing
        self.user    = self.config['DB_USER']
        self.passwd  = self.config['DB_PASSWD']
        self.host    = self.config['DB_HOST']
        self.db      = self.config['DB_DBNAME']
        cnx = mysql.connector.connect(user=self.user, password=self.passwd,
                                      host=self.host, database=self.db)
        cursor = cnx.cursor()
        query = ("select page_id,page_name,domain,target from performance_pages where status > 0")
        cursor.execute(query);
        controllers = {}
        for (page_id, page_name,domain,target) in cursor:
            controllers[page_name] = [page_id,target,domain,0]
        cursor.close()
        cnx.close()

        return controllers

    def clean_socks(self):
        """clean the socket and unix socks file"""
        self.client_sock.close()
        self.worker_sock.close()
        self.heartbeat_sock.close()
        self.log_sock.close()
        os.remove(self.config['MASTER_STATUS_SOCK'])
        os.remove(self.config['MASTER_PID'])
        self.kl_unregister()

__all__ = []
