"""
ISCSI Target Proxy
Mostly a toy to help better understand the ISCSI protocol
"""

import struct

import eventlet

# opcodes from http://www.ietf.org/rfc/rfc3720.txt
opcodes = {
    # Initiator opcodes
    0x00 : 'NOP-Out',
    0x01 : 'SCSI Command (encapsulates a SCSI Command Descriptor Block)',
    0x02 : 'SCSI Task Management function request',
    0x03 : 'Login Request',
    0x04 : 'Text Request',
    0x05 : 'SCSI Data-Out (for WRITE operations)',
    0x06 : 'Logout Request',
    0x10 : 'SNACK Request',
    # Target opcodes
    0x20 : 'NOP-In',
    0x21 : 'SCSI Response - contains SCSI status and possibly sense information or other response information.',
    0x22 : 'SCSI Task Management function response',
    0x23 : 'Login Response',
    0x24 : 'Text Response',
    0x25 : 'SCSI Data-In - for READ operations.',
    0x26 : 'Logout Response',
    0x31 : 'Ready To Transfer (R2T) - sent by target when it is ready to receive data.',
    0x32 : 'Asynchronous Message - sent by target to indicate certain special conditions.',
    0x3f : 'Reject',
}

def forward(srouce, dest, name, cb = lambda: None):
    while True:
        data = srouce.recv(32768)
        if data == '':
            cb()
            break
        # Figure out the Opcode
        header = data[:48]
        opcode = struct.unpack_from('B', header)[0] & 0x3f # ignore 1st 2 bits
        print '%s Opcode: %s (%s)' % (name, hex(opcode),
                opcodes.get(opcode, 'UNKNOWN'))
        # beware of ugly hack!
        if opcode == 0x24 and ':3260' in data:
            data = data.replace(':3260', ':6000')
        print data
        dest.sendall(data)

def closed_callback():
    print "Connection closed"

listener = eventlet.listen(('127.0.0.1', 6000))
while True:
    client, address = listener.accept()
    server = eventlet.connect(('127.0.0.1', 3260))
    eventlet.spawn_n(forward, client, server, 'INITIATOR', closed_callback)
    eventlet.spawn_n(forward, server, client, 'TARGET')
