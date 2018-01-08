# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import sys
import signal
import os
import time

def handler(signum, frame):
    print 'Signal handler called with signal', signum

def main():
    pid = os.fork()   
    print pid
    if pid > 0:
        sys.exit(0)
    signal.signal(signal.SIGUSR1, handler)
    signal.signal(signal.SIGUSR2, handler)
    signal.signal(signal.SIGHUP, handler)
    print 'My PID is:', os.getpid()
    while True:
        print 'Waiting....'
        time.sleep(3)

if __name__ == '__main__':
    sys.exit(main());

