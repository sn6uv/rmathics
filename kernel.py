# from __future__ import unicode_literals
import sys

from IPython.kernel.zmq.kernelbase import Kernel

from rmathics.version import version
from rmathics.expression import Expression, Symbol, String
from rmathics.definitions import Definitions
from rmathics.parser import parse
from rmathics.evaluation import evaluate

class MathicsKernel(Kernel):
    implementation = 'rmathics'
    implementation_version = version
    language = 'Wolfram'
    language_version = '10.0'
    language_info = {'mimetype': 'text/plain'}
    banner = 'Mathics is a general-purpose computer algebra system'

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        expr, messages = parse(code, definitions)
        if not silent:
            for message in messages:
                stream_content = {
                    'name': 'stderr',
                    'text': definition.construct_message(message),
                }
                self.send_response(self.iopub_socket, 'stream', stream_content)
        result, messages = evaluate(expr, definitions)
        if not silent:
            for message in messages:
                stream_content = {
                    'name': 'stderr',
                    'text': definition.construct_message(message),
                }
                self.send_response(self.iopub_socket, 'stream', stream_content)
            stream_content = {
                'name': 'stdout',
                'text': repr(result),
            }
            self.send_response(self.iopub_socket, 'stream', stream_content)
        return {
            'status': 'ok',
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
        }


def entry_point(argv):
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MathicsKernel)


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
