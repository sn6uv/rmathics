import os
import sys

from rzmq import zmq_init, zmq_socket, zmq_bind, ZMQ_REP, ZMQ_ROUTER, ZMQ_PUB, zmsg_t, zmq_msg_init, zmq_msg_recv, zmq_msg_close, zmq_msg_data, zmq_getsockopt, ZMQ_RCVMORE
from rpython.rtyper.lltypesystem import rffi


def read_contents(filename):
    fp = os.open(filename, os.O_RDONLY, 0o777)
    contents = ''
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        contents += read
    os.close(fp)
    return contents


class Connection(object):
    def __init__(self, contents):
        contents = contents.strip()
        if not (contents[0] == '{' and contents[-1] == '}'):
            raise ValueError("Invalid enclosing {}")
        for entry in self.lrstrip1(contents).split(','):
            field, value = entry.split(':')
            field = field.strip()
            value = value.strip()
            if not (field[0] == field[-1] == '"'):
                raise ValueError("Invalid field %s" % field)
            field = self.lrstrip1(field)
            if value[0] == value[-1] == '"':
                value = self.lrstrip1(value)
                if field == 'transport':
                    self.transport = value
                elif field == 'signature_scheme':
                    self.signature_scheme = value
                elif field == 'ip':
                    self.ip = value
                elif field == 'key':
                    self.key = value
                else:
                    raise ValueError("Unknown str field %s" % field)
            elif value.isdigit():
                value = int(value)
                if field == 'control_port':
                    self.control_port = value
                elif field == 'shell_port':
                    self.shell_port = value
                elif field == 'stdin_port':
                    self.stdin_port = value
                elif field == 'hb_port':
                    self.hb_port = value
                elif field == 'iopub_port':
                    self.iopub_port = value
                else:
                    raise ValueError("Unknown int field %s" % field)
            else:
                raise ValueError("Unknown value type %s" % value)

    @staticmethod
    def lrstrip1(s):
        '''
        returns s[1:-1]
        '''
        istart = 1
        istop = len(s) - 1
        assert istop >= 1
        return s[istart:istop]

    def debug(self):
        print(self.control_port, self.shell_port, self.transport,
              self.signature_scheme, self.stdin_port, self.hb_port, self.ip,
              self.iopub_port, self.key)

    def bind(self):
        self.ctx = zmq_init(1)
        base_endpoint = self.transport + '://' + self.ip + ':'

        self.hb = zmq_socket(self.ctx, ZMQ_REP)
        rc = zmq_bind(self.hb, base_endpoint + '%s' % self.hb_port)
        assert rc == 0

        self.shell = zmq_socket(self.ctx, ZMQ_ROUTER)
        rc = zmq_bind(self.shell, base_endpoint + '%s' % self.shell_port)
        assert rc == 0

        self.control = zmq_socket(self.ctx, ZMQ_ROUTER)
        rc = zmq_bind(self.control, base_endpoint + '%s' % self.control_port)
        assert rc == 0

        self.stdin = zmq_socket(self.ctx, ZMQ_ROUTER)
        rc = zmq_bind(self.stdin, base_endpoint + '%s' % self.stdin_port)
        assert rc == 0

        self.iopub = zmq_socket(self.ctx, ZMQ_PUB)
        rc = zmq_bind(self.iopub, base_endpoint + '%s' % self.iopub_port)
        assert rc == 0

    @staticmethod
    def msg_recv(socket):
        result = []
        morep = rffi.lltype.malloc(rffi.INTP.TO, 1, flavor='raw')
        morep[0] = rffi.r_int(1)

        more_sizep = rffi.lltype.malloc(rffi.UINTP.TO, 1, flavor='raw')
        more_sizep[0] = rffi.r_uint(rffi.sizeof(rffi.INT))

        while int(morep[0]):
            part = rffi.lltype.malloc(zmsg_t.TO, flavor='raw')
            rc = zmq_msg_init(part)
            assert rc == 0

            msg_size = zmq_msg_recv(part, socket, 0)
            assert msg_size != -1

            result.append(rffi.charpsize2str(zmq_msg_data(part), msg_size))

            rc = zmq_getsockopt(socket, ZMQ_RCVMORE, morep, more_sizep)
            assert rc == 0

            rc = zmq_msg_close(part)
            assert rc == 0

        return result

    @staticmethod
    def msg_send(socket, s):
        msg = rffi.lltype.malloc(zmsg_t.TO, flavor='raw')
        rc = zmq_msg_init_size(msg, len(s))
        assert rc == 0

        rffi.c_memcpy(zmq_msg_data(msg), s, len(s))
        msg_size = zmq_msg_send(msg, socket, 0)
        assert msg_size == len(s)


def entry_point(argv):
    if len(argv) != 2:
        return 1
    try:
        connection = Connection(read_contents(argv[1]))
    except ValueError:
        return 1
    connection.debug()
    connection.bind()
    print(connection.msg_recv(connection.shell))
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
