from rpython.translator.tool.cbuild import ExternalCompilationInfo
from rpython.rtyper.lltypesystem import rffi, lltype


info = ExternalCompilationInfo( includes=['zmq.h'], libraries=['zmq'])

zmq_init = rffi.llexternal("zmq_init", 
                           [rffi.INT], 
                           rffi.VOIDP,
                           compilation_info=info)

zmq_socket = rffi.llexternal("zmq_socket",
                             [rffi.VOIDP, rffi.INT],
                             rffi.VOIDP,
                             compilation_info=info)

zmq_bind = rffi.llexternal("zmq_bind",
                              [rffi.VOIDP, rffi.CCHARP],
                              rffi.INT,
                              compilation_info=info)

zmsg_t = rffi.COpaquePtr('zmq_msg_t', compilation_info=info)

zmq_msg_send = rffi.llexternal("zmq_msg_send",
                           [zmsg_t, rffi.VOIDP, rffi.INT],
                           rffi.INT,
                           compilation_info=info)

zmq_msg_recv = rffi.llexternal("zmq_msg_recv",
                           [zmsg_t, rffi.VOIDP, rffi.INT],
                           rffi.INT,
                           compilation_info=info)

zmq_msg_init_size = rffi.llexternal("zmq_msg_init_size",
                                    [zmsg_t, rffi.SIZE_T],
                                    rffi.SIZE_T,
                                    compilation_info=info)

zmq_msg_init = rffi.llexternal("zmq_msg_init",
                               [zmsg_t],
                               rffi.INT,
                               compilation_info=info)

zmq_msg_close = rffi.llexternal("zmq_msg_close",
                               [zmsg_t],
                               rffi.INT,
                               compilation_info=info)

zmq_msg_data = rffi.llexternal("zmq_msg_data",
                               [zmsg_t],
                               rffi.CCHARP,
                               compilation_info=info)

zmq_getsockopt = rffi.llexternal("zmq_getsockopt",
                               [rffi.VOIDP, rffi.INT, rffi.VOIDP, rffi.VOIDP],
                               rffi.INT,
                               compilation_info=info)

# it would be better to get these from the #define statements
ZMQ_PAIR = 0
ZMQ_PUB = 1
ZMQ_SUB = 2
ZMQ_REQ = 3
ZMQ_REP = 4
ZMQ_DEALER = 5
ZMQ_ROUTER = 6
ZMQ_PULL = 7
ZMQ_PUSH = 8
ZMQ_XPUB = 9
ZMQ_XSUB = 10
ZMQ_STREAM = 11

ZMQ_RCVMORE = 13
ZMQ_SNDMORE = 2

# def main(argv):
#     ctx = zmq_init(1)
#     socket = zmq_socket(ctx, 8)
#     zmq_connect(socket, "tcp://127.0.0.1:5555")
# 
#     #msg = malloc(sizeof(zmsg_t))
#     msg = rffi.lltype.malloc(zmsg_t.TO, flavor='raw')
# 
#     zmq_msg_init_size(msg, 5)
# 
#     #memcpy already available!
#     rffi.c_memcpy(zmq_msg_data(msg), "aaaaa", 5)
# 
#     for i in xrange(5000000):
#         zmq_send(socket, msg, 0)
# 
#     print 'Done!'
# 
#     return 0
# 
# def target(*args):
#     return main, None
