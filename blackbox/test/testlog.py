# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import logging

logging.basicConfig(
        filename='/tmp/test.log', 
        format = '%(asctime)s %(message)s',
        level=logging.DEBUG)
logging.debug('Test debug message')
logging.info('Test info message')
logging.warning('Test warning message')

pid=123
logging.info('pid is %s' % pid)


