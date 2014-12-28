# from __future__ import unicode_literals
import sys

try:
    import rpython
except ImportError:
    rpython = None

from rmathics.expression import Expression, Symbol, String
from rmathics.definitions import Definitions
from rmathics.parser import parse
from rmathics.evaluation import evaluate

def entry_point(argv):
    definitions = Definitions()
    # print(definitions.get_definition("$Context"))
    print(parse("1 + 2 3", definitions))
    # print(parse("1 + 2 + \:0030"))
    # print(parse("\\[Theta]", definitions))
    if not rpython:
        while True:
            x = raw_input(">> ")
            expr, messages = parse(x, definitions)
            for message in messages:
                print(message)
            result, messages = evaluate(expr, definitions)
            for message in messages:
                print(message)
            print(result)
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
