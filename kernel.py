import os
import sys

from rpython.rtyper.lltypesystem import rffi

from rmathics.parser import parse, WaitInputError
from rmathics.evaluation import evaluate
from rmathics.definitions import Definitions
from rmathics.kernel import rzmq, rjson, rlogging


rlogging.basicConfig(level=rlogging.INFO)


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
            field, value = entry.split(':', 1)
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
        self.execution_count = 1
        self.definitions = Definitions()

    @staticmethod
    def lrstrip1(s):
        '''
        returns s[1:-1]
        '''
        istart = 1
        istop = len(s) - 1
        assert istop >= 1
        return s[istart:istop]

    def bind(self):
        rlogging.info('binding sockets')
        self.ctx = rzmq.init(1)
        base_endpoint = self.transport + '://' + self.ip + ':'

        self.hb = rzmq.socket(self.ctx, rzmq.REP)
        rc = rzmq.bind(self.hb, base_endpoint + '%s' % self.hb_port)
        assert rc == 0

        self.shell = rzmq.socket(self.ctx, rzmq.ROUTER)
        rc = rzmq.bind(self.shell, base_endpoint + '%s' % self.shell_port)
        assert rc == 0

        self.control = rzmq.socket(self.ctx, rzmq.ROUTER)
        rc = rzmq.bind(self.control, base_endpoint + '%s' % self.control_port)
        assert rc == 0

        self.stdin = rzmq.socket(self.ctx, rzmq.ROUTER)
        rc = rzmq.bind(self.stdin, base_endpoint + '%s' % self.stdin_port)
        assert rc == 0

        self.iopub = rzmq.socket(self.ctx, rzmq.PUB)
        rc = rzmq.bind(self.iopub, base_endpoint + '%s' % self.iopub_port)
        assert rc == 0

    @staticmethod
    def msg_recv(socket):
        result = []
        morep = rffi.lltype.malloc(rffi.INTP.TO, 1, flavor='raw')
        morep[0] = rffi.r_int(1)

        more_sizep = rffi.lltype.malloc(rffi.UINTP.TO, 1, flavor='raw')
        more_sizep[0] = rffi.r_uint(rffi.sizeof(rffi.INT))

        while int(morep[0]):
            part = rffi.lltype.malloc(rzmq.zmsg_t.TO, flavor='raw')
            rc = rzmq.msg_init(part)
            assert rc == 0

            msg_size = rzmq.msg_recv(part, socket, 0)
            assert msg_size != -1

            result.append(rffi.charpsize2str(rzmq.msg_data(part), msg_size))

            rc = rzmq.getsockopt(socket, rzmq.RCVMORE, morep, more_sizep)
            assert rc == 0

            rc = rzmq.msg_close(part)
            assert rc == 0

        return result

    @staticmethod
    def msg_send(socket, parts):
        for i, part in enumerate(parts):
            msg = rffi.lltype.malloc(rzmq.zmsg_t.TO, flavor='raw')
            rc = rzmq.msg_init_size(msg, len(part))
            assert rc == 0

            rffi.c_memcpy(rzmq.msg_data(msg), part, len(part))

            if i < len(parts) - 1:
                msg_size = rzmq.msg_send(msg, socket, rzmq.SNDMORE)
            else:
                msg_size = rzmq.msg_send(msg, socket, 0)
            assert msg_size == len(part)

    def eventloop(self):
        while True:
            request = self.msg_recv(self.shell)

            self.msg_send(self.iopub, self.construct_message(   # report kernel busy
                request[0], request[3], '{"execution_state":"busy"}', 'status'))

            self.shell_msg(request)

            self.msg_send(self.iopub, self.construct_message(   # report kernel idle
                request[0], request[3], '{"execution_state":"idle"}', 'status'))

    def shell_msg(self, request):
        header = rjson.loads(request[3])
        msg_type = header['msg_type']._str
        if msg_type == 'kernel_info_request':
            response = self.construct_message(request[0], request[3],
                                              self.kernel_info(),
                                              'kernel_info_reply')
            self.msg_send(self.shell, response)
        elif msg_type == 'execute_request':
            content = rjson.loads(request[6])
            code = content['code']._str

            # Parse
            try:
                expr, messages = parse(code, self.definitions)
            except WaitInputError:
                expr, messages = None, [('Syntax', 'sntup')]

            for message in messages:
                error = rjson.JDict({       # FIXME
                    "ename": rjson.JStr(message[0]),
                    "evalue": rjson.JStr(message[1]),
                    "traceback": rjson.JList([]),
                }).dumps()
                error_response = self.construct_message(
                    request[0], request[3], error, 'error')
                self.msg_send(self.iopub, error_response)

            # Evaluate
            if expr is not None:
                result, messages = evaluate(expr, self.definitions)
                for message in messages:
                    error = rjson.JDict({       # FIXME
                        "ename": rjson.JStr(message[0]),
                        "evalue": rjson.JStr(message[1]),
                        "traceback": rjson.JList([]),
                    }).dumps()
                    error_response = self.construct_message(
                        request[0], request[3], error, 'error')
                    self.msg_send(self.iopub, error_response)

                execute_result = rjson.JDict({
                    "execution_count": rjson.JInt(self.execution_count),
                    "data": rjson.JDict({'text/plain': rjson.JStr(result.repr())}),
                    "metadata": rjson.JDict({}),
                }).dumps()
                result_response = self.construct_message(
                    request[0], request[3], execute_result, 'execute_result')
                self.msg_send(self.iopub, result_response)

                execute_reply = rjson.JDict({
                    "status": rjson.JStr("ok"),
                    "execution_count": rjson.JInt(self.execution_count),
                    "user_expressions": rjson.JDict({}),
                    "payload": rjson.JList([]),
                }).dumps()
                reply_response = self.construct_message(
                    request[0], request[3], execute_reply, 'execute_reply')
                self.msg_send(self.shell, reply_response)
                self.execution_count += 1
        else:
            rlogging.warn("Ignoring msg %s" % msg_type)

    def construct_message(self, zmq_identity, parent, content, msg_type):
        rlogging.debug('construct_message(' +' ,'.join([zmq_identity, parent, content, msg_type]) + ')')
        header = rjson.JDict({
            'msg_id': rjson.JStr('8fdb7d8e-8be3-44c6-9579-3f1d646bb097'),
            'username': rjson.JStr('angus'),
            'session': rjson.JStr(zmq_identity),
            'msg_type': rjson.JStr(msg_type),
            'version': rjson.JStr('5.0'),
        })
        metadata = '{}'
        sig = ''        # TODO
        response = [
            zmq_identity,       # zmq identity(ies)
            '<IDS|MSG>',        # delimiter
            sig,                # HMAC signature
            header.dumps(),     # header
            parent,             # parent_header
            metadata,           # serialized metadata dict
            content,            # serialized content dict
            '{}',               # extra eaw data buffer(s)
        ]
        return response

    def kernel_info(self):
        content = rjson.JDict({
            'protocol_version': rjson.JStr('5.0'),
            'implementation': rjson.JStr('rmathics'),
            'implementation_version': rjson.JStr('0.0.1'),
            'language_info': rjson.JDict({
                'name': rjson.JStr('mathics'),
                'version': rjson.JStr('1.0.0'),
                'mimetype': rjson.JStr('application/mathics'),
                'file_extension': rjson.JStr('m'),
                # 'pygarments_lexer': rjson.JStr('???'),
                # 'codemirror_code': rjson.JStr('???'),
                # 'nbconvert_exporter': rjson.JStr('???'),
            }),
            'banner': rjson.JStr('RPYTHON MATHICS'),
        })
        return content.dumps()


def entry_point(argv):
    if len(argv) != 2:
        return 1
    try:
        connection = Connection(read_contents(argv[1]))
    except ValueError:
        return 1
    connection.bind()

    rlogging.info(str((
        connection.control_port, connection.shell_port, connection.transport,
        connection.signature_scheme, connection.stdin_port, connection.hb_port,
        connection.ip, connection.iopub_port, connection.key)))

    connection.eventloop()
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
