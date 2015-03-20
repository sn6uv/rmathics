from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.rtyper.lltypesystem import rffi, lltype


info = ExternalCompilationInfo(includes=['zmq.h'], libraries=['zmq'])

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

zmsg_t = rffi.COpaquePtr('zmq_msg_t', compilation_info=info)

msg_send = rffi.llexternal("zmq_msg_send",
                               [zmsg_t, rffi.VOIDP, rffi.INT],
                               rffi.INT,
                               compilation_info=info)

msg_recv = rffi.llexternal("zmq_msg_recv",
                               [zmsg_t, rffi.VOIDP, rffi.INT],
                               rffi.INT,
                               compilation_info=info)

msg_init_size = rffi.llexternal("zmq_msg_init_size",
                                    [zmsg_t, rffi.SIZE_T],
                                    rffi.SIZE_T,
                                    compilation_info=info)

msg_init = rffi.llexternal("zmq_msg_init",
                               [zmsg_t],
                               rffi.INT,
                               compilation_info=info)

msg_close = rffi.llexternal("zmq_msg_close",
                                [zmsg_t],
                                rffi.INT,
                                compilation_info=info)

msg_data = rffi.llexternal("zmq_msg_data",
                               [zmsg_t],
                               rffi.CCHARP,
                               compilation_info=info)

getsockopt = rffi.llexternal("zmq_getsockopt",
                                 [rffi.VOIDP, rffi.INT, rffi.VOIDP, rffi.VOIDP],
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
