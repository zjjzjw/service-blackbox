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

sock.connect('tcp://127.0.0.1:7555')

data = {
    "controller_name": "test_page",
    "unload" : 100 ,
    "redirect" : 100,
    "dns" : 100 ,
    "tcp" : 100,
    "request" : 100,
    "response" : 100,
    "processing" : 100,
    "load" : 100,
    "kpi_dom" : 100,
    "kpi_onload" : 100,
    "kpi_d2d"  : 100
}

while True:
    frames = ['v1', '\x00', packb(time()), r'', packb(json.dumps(data))]
    print frames
    sock.send_multipart(frames)
    sleep(0.5)
