# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import zmq
import msgpack
import time

from device import config

VERSION = r'V1'
EMPTY = r''

def millitime():
    return int(round(time.time() * 1000))

class Reload:
    def __init__(self):
        self.rep = config.Config().reload_endpoint

        context = zmq.Context()
        self.reload_socket = zmq.Socket(context, zmq.PUSH)
        self.reload_socket.connect(self.rep)

    def run(self):
        frames = self.build_reload_msg()
        
        self.reload_socket.send_multipart(frames)
        self.reload_socket.close()
    
    def build_reload_msg(self):
        now = millitime()

        frames = [VERSION, '\x04', str(now), EMPTY, 'reload']
        
        return frames

def main():
    reload = Reload()
    reload.run()

if __name__ == '__main__':
    main()
    

  
        