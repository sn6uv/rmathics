from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.rtyper.lltypesystem import rffi, lltype
from rpython.rtyper.tool import rffi_platform

info = ExternalCompilationInfo(includes=['zmq.h'], libraries=['zmq'])


class CConfig(object):
    _compilation_info_ = info
    pollitem_t = rffi_platform.Struct(
        'zmq_pollitem_t',
        [('socket', rffi.VOIDP), ('fd', rffi.INT), ('events', rffi.SHORT), ('revents', rffi.SHORT)])


globals().update(rffi_platform.configure(CConfig))


init = rffi.llexternal("zmq_init",
                       [rffi.INT],
                       rffi.VOIDP,
                       compilation_info=info)

socket = rffi.llexternal("zmq_socket",
                         [rffi.VOIDP, rffi.INT],
                         rffi.VOIDP,
                         compilation_info=info)

bind = rffi.llexternal("zmq_bind",
                       [rffi.VOIDP, rffi.CCHARP],
                       rffi.INT,
                       compilation_info=info)

msg_t = rffi.COpaquePtr('zmq_msg_t', compilation_info=info)

msg_send = rffi.llexternal("zmq_msg_send",
                           [msg_t, rffi.VOIDP, rffi.INT],
                           rffi.INT,
                           compilation_info=info)

msg_recv = rffi.llexternal("zmq_msg_recv",
                           [msg_t, rffi.VOIDP, rffi.INT],
                           rffi.INT,
                           compilation_info=info)

msg_init_size = rffi.llexternal("zmq_msg_init_size",
                                [msg_t, rffi.SIZE_T],
                                rffi.SIZE_T,
                                compilation_info=info)

msg_init = rffi.llexternal("zmq_msg_init",
                           [msg_t],
                           rffi.INT,
                           compilation_info=info)

msg_close = rffi.llexternal("zmq_msg_close",
                            [msg_t],
                            rffi.INT,
                            compilation_info=info)

msg_data = rffi.llexternal("zmq_msg_data",
                           [msg_t],
                           rffi.CCHARP,
                           compilation_info=info)

getsockopt = rffi.llexternal("zmq_getsockopt",
                             [rffi.VOIDP, rffi.INT, rffi.VOIDP, rffi.VOIDP],
                             rffi.INT,
                             compilation_info=info)

poll = rffi.llexternal("zmq_poll",
                       [rffi.lltype.Ptr(pollitem_t), rffi.INT, rffi.LONG],
                       rffi.INT,
                       compilation_info=info)

# it would be better to get these from the #define statements
PAIR = 0
PUB = 1
SUB = 2
REQ = 3
REP = 4
DEALER = 5
ROUTER = 6
PULL = 7
PUSH = 8
XPUB = 9
XSUB = 10
STREAM = 11

RCVMORE = 13
SNDMORE = 2

POLLIN = 1
POLLOUT = 2
POLLERR = 3
