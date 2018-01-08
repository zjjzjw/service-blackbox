# -*- coding: utf-8 -*-
import argparse
import errno
from json import loads as json_loads, dumps as json_dumps
from logging import INFO
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler
import os
import random
import subprocess
from signal import SIGHUP, SIGINT, SIGQUIT, SIGTERM, SIGUSR1, signal
import sys
import time

from msgpack import packb, unpackb
import mysql.connector
import zmq

from blackbox import BaseApplication
from blackbox.util.helpers import millitime



VERSION = r'V1.0'
EMPTY = r''

class Worker(BaseApplication):

    QUEUE_SIGS = [SIGQUIT, SIGINT, SIGTERM, SIGUSR1, SIGHUP]

    EXIT_SIGS = [SIGQUIT, SIGINT, SIGTERM]

    SIG_QUEUE = []

    def __init__(self, import_name, controller):

        super(Worker, self).__init__(import_name)

        # read config
        from blackbox import default_settings
        self.config.from_object(default_settings)

        self.read_config()

        page_id, domain ,controller ,target = controller.split("-")

        self.page_id    = page_id
        self.domain = domain
        self.controller = controller 
        self.target     = target
        

        self.last_push   = 0
        self.last_insert = time.strftime("%M", time.localtime(time.time()))

         
        self.unload = [] 
        self.redirect =[]
        self.dns = []
        self.tcp = [] 
        self.request = []
        self.response = []
        self.processing = []
        self.load = [] 
        self.kpi_dom = []
        self.kpi_onload = [] 
        self.kpi_domparsing = []
        

        self.created         = 0


        self.quit            = False

        if not self.debug:
            formatter = Formatter(self.config['LOG_FORMAT'])
            handler = TimedRotatingFileHandler(self.config['WORKER_LOG'],
                                               when='midnight')
            handler.setLevel(INFO)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def read_config(self):
        """read config file in order

        ~/.blackbox.cfg
        /etc/blackbox.cfg/
        """
        path = os.path.abspath(os.path.expanduser('~/.blackbox.cfg'))
        if os.path.isfile(path):
            self.config.from_pyfile(path)
            return

        path = '/etc/blackbox.cfg'
        if os.path.isfile(path):
            self.config.from_pyfile(path)

    def start(self):
        """prepare the socks, return self to run join"""

        def _handle(sig, frames):
            self.SIG_QUEUE.append(sig)

        for sig in self.QUEUE_SIGS:
            signal(sig, _handle)

        ctx = zmq.Context()

        self.sub = zmq.Socket(ctx, zmq.SUB)
        self.sub.setsockopt(zmq.SUBSCRIBE, "{}-{}-{}".format(self.page_id,self.domain,
                                                          self.controller))
        self.sub.connect(self.config['WORKER_SOCK'])

        self.heartbeat_socket = zmq.Socket(ctx, zmq.PUSH)
        self.heartbeat_socket.connect(self.config['HEARTBEAT_SOCK'])

        self.db_conn = self.connect_db()
        self.cursor = self.db_conn.cursor()

        poller = zmq.Poller()
        poller.register(self.sub, zmq.POLLIN)
        self.poller = poller

        return self

    def work(self):
        """poll messages from sub sock"""
        events = []
        try:
            events = self.poller.poll(self.config['POLLER_INTERVAL'])
        except zmq.ZMQError as e:
            if e.errno == errno.EINTR:
                return
            else:
                pass
        except Exception as e:
            import traceback
            traceback.print_exc()

        for socket, flags in events:
            if socket == self.sub:
                print(self.domain + "-" + self.controller);
                try:
                    self.handle_request()
                except: # TODO capture exact error
                    import traceback
                    self.logger.error(traceback.format_exc())
            else:
                assert False

        try:
            self.push_heartbeat()
        except: # TODO: capture exact error
            import traceback
            traceback.print_exc()
            self.logger.error(("{} : push heartbeat "
                               "error").format(self.controller))

    def join(self):
        """main loop"""
        self.start_time = millitime()

        while True:

            if len(self.SIG_QUEUE) > 0:
                # signal handling
                sig = self.SIG_QUEUE.pop(0)
                if sig in self.EXIT_SIGS:
                    self.logger.info("worker {} closed".format(self.controller))
                    self.close()
                    os._exit(0)
            else:
                self.work()

    def handle_request(self):
        try:
            frames = self.sub.recv_multipart(zmq.NOBLOCK)
        except:
            pass

        i = frames.index(EMPTY)

        json_str = unpackb(frames[i + 1])
        data = json_loads(json_str)
        
        self.gather_unload_time(data)
        self.gather_redirect_time(data)
        self.gather_dns_time(data)
        self.gather_tcp_time(data)
        self.gather_request_time(data)
        self.gather_response_time(data)
        self.gather_processing_time(data)
        self.gather_load_time(data)
        self.gather_kpi_onload_time(data)
        self.gather_kpi_dom_time(data)
        self.gather_kpi_domparsing_time(data)
        

        now = time.strftime("%M", time.localtime(time.time()))
        if (int(now) - int(self.last_insert) == 1) or\
            (int(now) - int(self.last_insert) == -59):
            self.insert_data()
            self.last_insert = now
        elif int(now) - int(self.last_insert) <> 0:
            self.last_insert = now

    def gather_unload_time(self,data):
        self.unload.append(int(data["uls"]) - int(data["ele"]))

    def gather_redirect_time(self, data):
        self.redirect.append(int(data["re"]) - int(data["rs"]))

    def gather_dns_time(self, data):
        self.dns.append(int(data["le"]) - int(data["le"]))
    
    def gather_tcp_time(self, data):
        self.tcp.append(int(data["ce"]) - int(data["cs"]));

    def gather_request_time(self ,data):
        if int(data["rqs"]) == 0  or data["rqs"] == "None" :
           self.request.append(0)
        else :
           self.request.append(int(data["rps"]) - int(data["rqs"]))
        
    def gather_response_time(self ,data):
        self.response.append(int(data["rpe"]) - int(data["rps"]))

    def gather_processing_time(self ,data):
        self.processing.append(int(data["dc"]) - int(data["dl"]))

    def gather_load_time(self ,data):
        self.load.append(int(data["lde"]) - int(data["lds"]))
    
    def gather_kpi_dom_time(self ,data):
        if int(data["rs"]) == 0 :
           self.kpi_dom.append(int(data["cle"]) - int(data["fs"]))
        else:
           self.kpi_dom.append(int(data["cle"]) - int(data["rs"]))
    
    def gather_kpi_onload_time(self ,data):
        if int(data["rs"]) == 0 :
           self.kpi_onload.append(int(data["lde"]) - int(data["fs"]))
        else:
           self.kpi_onload.append(int(data["lde"]) - int(data["rs"]))

    def gather_kpi_domparsing_time(self ,data):
        self.kpi_domparsing.append(int(data['cls']) - int(data["dl"]))
    
    def insert_lower_data(self,data):
        now = time.time();
        unload_time =int(data["uls"]) - int(data["ele"])
        redirect_time = int(data["re"]) - int(data["rs"])
        dns_time =int(data["le"]) - int(data["le"])
        tcp_time =int(data["ce"]) - int(data["cs"])
        request_time = int(data["rps"]) - int(data["rqs"])
        response_time =int(data["rpe"]) - int(data["rps"])
        processing_time =int(data["dc"]) - int(data["dl"])
        load_time = int(data["lde"]) - int(data["lds"])
        kpi_dom_time =int(data["cle"]) - int(data["rs"])
        kpi_onload_time = int(data["lde"]) - int(data["rs"])
        kpi_domparsing_time = int(data['cls']) - int(data["dl"])
        created_time = self.get_created_time(now)
        ip = data['ip']
        ymd = time.strftime("%Y%m%d", time.localtime(now - 60))
      
        sql = (
            "insert into "
            "performance_lower_data "
            "(page_id, page_name, unload_time, redirect_time, "
            "dns_time ,tcp_time , request_time ,response_time ,processing_time, "
            "load_time ,kpi_dom_time,kpi_onload_time ,kpi_domparsing_time, "
            "created ,ip, ymd )"
            "values "
            "('{}', '{}', '{}', '{}', '{}', '{}', '{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')"
        ).format(self.page_id,self.controller,unload_time,redirect_time,
                 dns_time, tcp_time,request_time,response_time,processing_time,
                 load_time,kpi_dom_time,kpi_onload_time,kpi_domparsing_time,
                 str(created_time),ip,ymd)
        self.logger.info(sql)
        self.insert(sql)
        self.logger.info(("{} insert data into performance_lower_data "
                         "success").format(self.controller))


    def insert_data(self):
        now = time.time()
        self.insert_page_time(now)

    def insert_page_time(self, now):
        self.logger.info("%s begin handle page time" % self.controller)
        
        self.unload.sort()
        unload_time = self.unload[int(len(self.unload)*self.config['STANDARD'])]
        
        self.redirect.sort()
        redirect_time = self.redirect[int(len(self.redirect)*self.config['STANDARD'])]
        
        self.dns.sort()
        dns_time = self.dns[int(len(self.dns)*self.config['STANDARD'])]
        
        self.tcp.sort()
        tcp_time = self.tcp[int(len(self.tcp)*self.config['STANDARD'])]
        
        self.request.sort()
        request_time = self.request[int(len(self.request)*self.config['STANDARD'])]
        
        self.response.sort()
        response_time = self.response[int(len(self.response)*self.config['STANDARD'])]
        
        self.processing.sort()
        processing_time = self.processing[int(len(self.processing)*self.config['STANDARD'])]
        
        self.load.sort()
        load_time = self.load[int(len(self.load)*self.config['STANDARD'])]
        
        self.kpi_dom.sort()
        kpi_dom_time = self.kpi_dom[int(len(self.kpi_dom)*self.config['STANDARD'])]
        
        
        self.kpi_onload.sort()
        kpi_onload_time = self.kpi_onload[int(len(self.kpi_onload)*self.config['STANDARD'])]
        

        self.kpi_domparsing.sort()
        kpi_domparsing_time = self.kpi_domparsing[int(len(self.kpi_domparsing)*self.config['STANDARD'])]

        created_time = self.get_created_time(now)
        ymd = time.strftime("%Y%m%d", time.localtime(now - 60))

        sql = (
            "insert into "
            "performance_minutes_data "
            "(page_id, page_name, unload_time, redirect_time, "
            "dns_time ,tcp_time , request_time ,response_time ,processing_time, "
            "load_time ,kpi_dom_time,kpi_onload_time ,kpi_domparsing_time, "
            "created , ymd , dimensions) "
            "values "
            "('{}', '{}', '{}', '{}', '{}', '{}', '{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')"
        ).format(self.page_id,self.controller,unload_time,redirect_time,
              dns_time, tcp_time,request_time,response_time,processing_time,
                 load_time,kpi_dom_time,kpi_onload_time,kpi_domparsing_time,
                 str(created_time), ymd ,1)
        self.logger.info(sql)
        self.insert(sql)
        self.logger.info(("{} insert data into performance_minutes_data "
                         "success").format(self.controller))
        self.log_sort_data(now)
        #clear data
        self.unload = [] 
        self.redirect =[]
        self.dns = []
        self.tcp = [] 
        self.request = []
        self.response = []
        self.processing = []
        self.load = [] 
        self.kpi_dom = []
        self.kpi_onload = [] 
        self.kpi_domparsing = []
    
    def log_sort_data(self,now):    
        created_time = self.get_created_time(now)
        ymd = time.strftime("%Y%m%d", time.localtime(now - 60)) 
        length = len(self.unload)       
        data_str_list = []
        data_str_list.append("{}{}".format(str(created_time),"\n"))
        for i in range(0,length):       
           unload_time = self.unload[i]    
           redirect_time = self.redirect[i]
           dns_time = self.dns[i]          
           tcp_time = self.tcp[i]          
           request_time = self.request[i]  
           response_time = self.response[i]
           processing_time = self.processing[i]
           load_time = self.load[i]        
           kpi_dom_time = self.kpi_dom[i]  
           kpi_onload_time = self.kpi_onload[i]
           kpi_domparsing_time = self.kpi_domparsing[i]  
  
           data_str_list.append(("{},{},{},{},"
                                "{},{},{},{},{},"               
                                "{},{},{},{},"                  
                                "{},{}\n").format(self.page_id,self.controller,unload_time,redirect_time,
                                dns_time, tcp_time,request_time,response_time,processing_time,
                                load_time,kpi_dom_time,kpi_onload_time,kpi_domparsing_time,
                                str(created_time),ymd))
        data_str = "".join(data_str_list)
        print(data_str)
        #subprocess.call(['/root/blackbox/blackbox/write_log.sh',str(data_str)]);

    def connect_db(self):
        _ = mysql.connector.connect(user=self.config['DB_USER'],
                                    password=self.config['DB_PASSWD'],
                                    host=self.config['DB_HOST'],
                                    database=self.config['DB_DBNAME'])
        return _

    def insert(self, sql_str):
        try:
            self.cursor.execute(sql_str)
            self.db_conn.commit()
        except: # TODO: capture exact error
            import traceback
            self.logger.error(traceback.format_exc())

    def push_heartbeat(self):
        now = millitime()
        if now - self.last_push > self.config['HEARTBEAT_INTERVAL']:
            frames = self.build_heartbeat(now)
            self.heartbeat_socket.send_multipart(frames)
            self.last_push = now

    def build_heartbeat(self, now):
        frames = [VERSION, '\x03', packb(now), EMPTY, packb(self.controller)]
        return frames

    def get_created_time(self, now):
        created_time = time.strftime("%Y-%m-%d %H:%M:00",
                                     time.localtime(now - 60))
        return created_time

    def sampling(self, execution_time):
        multiple = execution_time / float(self.target)
        if multiple >= 3:
            multiple = 3

        p = multiple / 3
        sample = 0
        if p > random.random():
            sample = 1
        else:
            sample = 0

        return sample

    def quit(self):
        self.logger.info("%s closed" % self.controller)
        self.close()
        os._exit(0)

    def close(self):
        self.heartbeat_socket.close()
        self.sub.close()
        self.cursor.close()
        self.db_conn.close()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-c', '--controller', help='controller name')
    options = ap.parse_args()
    worker = Worker(__name__, controller=options.controller)
    worker.start().join()

if __name__ == '__main__':
    sys.exit(main())
