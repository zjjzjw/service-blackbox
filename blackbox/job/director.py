# -*- coding: utf-8 -*-

import getopt
import logging
import sys
import time
import subprocess
import os
from device import config
from classes import connector 

class Director():
    def __init__(self, options):
        self.options = options
        self.config = config.Config()
        self.connector = connector.Connector(self.config.user, self.config.passwd, self.config.host, self.config.database)
        
    def run(self):
        try:
            self.get_pageIds()
            self.create_analysts()
        except:
            logging.info("director error")
        finally:
            self.connector.close()
            os._exit(0)
    
    def get_pageIds(self):
        sql_str = "select page_id, controller_name from pages where status = 1"
        self.connector.query(sql_str)
        
    def create_analyst(self, page_id, controller_name, date):
        subprocess.Popen([self.config.interpreter, os.path.dirname(__file__) + '/analyst.py', '-c' + controller_name, '-p' + str(page_id), '-d' + str(date)])
        
    def create_analysts(self):
        for (page_id, controller_name) in self.connector.cursor:
            self.create_analyst(page_id, controller_name, self.options.date)

class Options:
    """
options:
    -h, --help
        Show this help message and exit

    -d, --date
        date that will be analysed. like this 20120320
    """
    def __init__(self, argv):
        self.prog   =os.path.basename(argv[0])

        self.date = time.strftime("%Y%m%d", time.localtime(time.time() - 86400))                    # date

        try:
            self.parse(argv)
        except:
            self.usage()
            return

    def parse(self, argv):
        opts, self.args = getopt.getopt(argv[1:], 'hd:', ['help', 'date='])

        for o, value in opts:
            if o in ('-h', '--help'):
                self.usage()
                return
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
    
    logging.info("start analysis date for %s" % options.date)
    print "start analysis date for %s" % options.date
    
    director = Director(options)
    director.run()

if __name__ == '__main__':
    sys.exit(main())
        