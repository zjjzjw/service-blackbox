# -*- coding: utf-8 -*-

import zmq
import msgpack

context = zmq.Context()
subscriber = zmq.Socket(context, zmq.SUB)
fil = ''
subscriber.setsockopt(zmq.SUBSCRIBE, fil)
subscriber.connect("ipc:///tmp/worker.ipc")

while True:
    frames = subscriber.recv_multipart()
    i = frames.index('')
    print i
    print frames[i+1]
