# -*- coding: utf-8 -*-

import getopt
import logging
import sys
import datetime
import subprocess
import os
from device import config
from classes import connector 
        
def main():
    today = datetime.datetime.today()
    ago = today - datetime.timedelta(days=30)
    ruler = int(ago.strftime('%Y%m%d0000'))

    conn = connector.Connector("black_box_rx", "black_box", "10.10.8.35", "black_box")
    sql_str = "select id, minute from slow_requests order by id limit 1"
    del_str = "delete from slow_requests order by id limit 10000"
    while True:
        conn.query(sql_str)
        id, minute = conn.cursor.fetchone()

        print ruler
        print int(minute) < ruler
        if int(minute) < ruler:
            print "%s going on..." % minute
            # try:
            #     conn.cursor.execute(del_str)
            #     conn.cnn.commit()
            # except:
            #     conn.cnn.rollback()
            #     raise
        else:
            print "%s done." % minute
            sys.exit()

if __name__ == '__main__':
    sys.exit(main())
        