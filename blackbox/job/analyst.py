# -*- coding: utf-8 -*-

import getopt
import json
import logging
import time
import sys
import os
from device import config
from classes import connector

class Analyst:
    def __init__(self, options):
        self.options = options
        self.config = config.Config()
        self.connector = connector.Connector(self.config.user, self.config.passwd, self.config.host, self.config.database)
        
        self.app_time = {}
        self.frame_time = {}
        self.module_time = {}
        self.execution_time = {}
        self.slow_requests = ""
        self.content = {}
        self.sql_count = 0
        
    def run(self):
        try:
            if self.check_is_exist() > 0:
                print "this job had been run: page_id = %s " % str(self.options.page_id)
            else:
                self.get_data()
                self.insert_data()
                print "%s run success" % str(self.options.page_id)
        except:
            print "analyst: %s run error" % self.options.controller_name
        finally:
            self.connector.close()
            os._exit(0)
    
    def insert_data(self):
        self.insert_page_everyday_analysis()
        self.inser_sql_everyday_analysis()
    
    def insert_page_everyday_analysis(self):
        self.analysis_data(self.app_time)
        self.analysis_data(self.frame_time)
        self.analysis_data(self.module_time)
        self.analysis_data(self.execution_time)
        self.analysis_data(self.content)
        
        values = "(" + str(self.options.page_id) + ",'" + json.dumps(self.app_time) + "','" + json.dumps(self.frame_time) + "','" + json.dumps(self.module_time) + "','" + json.dumps(self.execution_time) + "','" + json.dumps(self.content) + "','" + json.dumps(self.slow_requests) + "'," + str(self.options.date) + ")"          
        sql_str = "insert into everyday_analysis (page_id, app_time, frame_time, module_time, execution_time, content, slow_requests, date) values " + values 
        
        self.connector.query(sql_str)
    
    def inser_sql_everyday_analysis(self):
        sql_str = "insert into sql_everyday_analysis (page_id, count, date) values (" + str(self.options.page_id) + "," + str(self.sql_count) + "," + str(self.options.date) + ")"
        self.connector.query(sql_str)
        
    def analysis_data(self, data):
        for key in data:
            data[key].sort()
            data[key] = data[key][int(len(data[key]) * self.config.standard)]
    
    def get_data(self):
        self.get_page_time()
        self.get_slow_requests()
        self.get_content()
        self.get_sql_count()
        
    def get_sql_count(self):
        sql_str = "select count from sql_count where page_id = " + str(self.options.page_id) + " and minute like '" + str(self.options.date) + "____'"
        self.connector.query(sql_str)
        
        for (count, ) in self.connector.cursor:
            self.sql_count += count
        
    def get_content(self):
        created_day = str(self.options.date)[0:4] + "-" + str(self.options.date)[4:6] + "-" + str(self.options.date)[6:8] + " __:__:__"
        sql_str = "select content from slow_requests_analysis where page_id = " + str(self.options.page_id) + " and created like '" + created_day + "'"
        self.connector.query(sql_str)
        
        for (content, ) in self.connector.cursor:
            self.gather_data(self.content, json.loads(content))
        
    def get_slow_requests(self):
        sql_str = "select count(id) from slow_requests where page_id = " + str(self.options.page_id) + " and minute like '" + str(self.options.date) + "____'"
        self.connector.query(sql_str)
        
        n = 0
        for (count, ) in self.connector.cursor:
            n = count - int(count * self.config.standard)
        m = 30
        
        sql_str = "select id from slow_requests where page_id = " + str(self.options.page_id) + " and minute like '" + str(self.options.date) + "____' order by execution_time DESC limit " + str(n) + "," + str(m)
        self.connector.query(sql_str)
        
        for (id, ) in self.connector.cursor:
            if self.slow_requests == "":
                self.slow_requests += str(id)
            else:
                self.slow_requests = self.slow_requests + "." +  str(id) 
        
    def get_page_time(self):
        sql_str = "select app_time, module_time, frame_time, execution_time from page_time where page_id = " + str(self.options.page_id) + " and date = " + str(self.options.date)
        self.connector.query(sql_str)
        
        for (app_time, module_time, frame_time, execution_time) in self.connector.cursor:   
            self.gather_data(self.app_time, json.loads(app_time))
            self.gather_data(self.module_time, json.loads(module_time))
            self.gather_data(self.frame_time, json.loads(frame_time))
            self.gather_data(self.execution_time, json.loads(execution_time))
        
    def gather_data(self, out, data):
        for key in data:
            if out.has_key(key):
                out[str(key)].append(data[key])
            else:
                out[str(key)] = [data[key]]
                
    def check_is_exist(self):
        sql_str = "select id from everyday_analysis where page_id = " + str(self.options.page_id) + " and date = " + str(self.options.date)
        self.connector.query(sql_str)
        
        exist = 0
        for (n, ) in self.connector.cursor:
            exist = n
            
        return exist
        
class Options:
    """
options:
    -h, --help
        Show this help message and exit

    -c, --controller_name
        controller name

    -p, --pageid
        page_id
        
    -d, --date
    date that will be analysed. like this 20120320
    """
    def __init__(self, argv):
        self.prog   =os.path.basename(argv[0])

        self.controller_name        = ""                                                            # controller_name
        self.page_id                = 0                                                             # page id
        self.date                   = time.strftime("%Y%m%d", time.localtime(time.time() - 86400))  #date

        try:
            self.parse(argv)
        except:
            self.usage()
            return

    def parse(self, argv):
        opts, self.args = getopt.getopt(argv[1:], 'hc:p:d:', ['help', 'controller_name=', 'pageid=', 'date='])

        for o, value in opts:
            if o in ('-h', '--help'):
                self.usage()
                return
            elif o in ('-c', '--controller_name'):
                self.controller_name = value
            elif o in ('-p', '--pageid'):
                self.page_id = value
            elif o in ('-d', '--date'):
                self.date = value
            else:
                pass

    def usage(self):
        print('usage: %s [options] <worker command line>' % self.prog)
        print self.__doc__
               
def main():
    logging.basicConfig(
        filename = '/tmp/all_day_Analysis.log',
        format = '%(asctime)s %(message)s',
        level = logging.INFO
    )
    
    options = Options(sys.argv)
    analyst = Analyst(options)
    analyst.run()

if __name__ == '__main__':
    sys.exit(main())
