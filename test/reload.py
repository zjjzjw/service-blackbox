# -*- coding: utf-8 -*-
import json
from socket import gethostname
from time import sleep, time


from msgpack import packb
import zmq

ctx = zmq.Context().instance()

sock = ctx.socket(zmq.PUSH)
sock.setsockopt(zmq.LINGER, 0)
sock.setsockopt(zmq.SNDHWM, 5)

sock.connect('tcp://127.0.0.1:7556')

frames = ['v1', '\x04', packb(time()), r'']
print frames
sock.send_multipart(frames)
sleep(0.5)
