import struct

import eventlet


def forward(srouce, dest, cb = lambda: None):
    while True:
        data = srouce.recv()
        if data == '':
            cb()
            break
        # TODO: interpret iscsi packets here
        # beware of ugly hack!
        if ':3260' in data:
            data = data.replace(':3260', ':6000')
        print data
        dest.sendall(data)

def closed_callback():
    print "Connection closed"

listener = eventlet.listen(('127.0.0.1', 6000))
while True:
    client, address = listener.accept()
    server = eventlet.connect(('127.0.0.1', 3260))
    eventlet.spawn_n(forward, client, server, closed_callback)
    eventlet.spawn_n(forward, server, client)
