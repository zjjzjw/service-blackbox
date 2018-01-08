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
    "controller_name": "Listing_Property_SearchSaleController",
    "app_name": gethostname(),
    "execution_time": 199,
    "module_time": {"mysql": 100, "memcached": 20},
    "frame_time": {"controller": 55, "page": 60, "component": 32},
    "url": "shanghai.anjuke.com",
    "user_defined": {"CP1": 111},
    "sql_count": 1
}

while True:
    frames = ['v1', '\x00', packb(time()), r'', packb(json.dumps(data))]
    print frames
    sock.send_multipart(frames)
    sleep(0.5)
