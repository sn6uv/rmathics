from __future__ import unicode_literals
import sys
from rmathics.expression import Expression, Symbol, String
from rmathics.definitions import Definitions
from rmathics.rules import *
from rmathics.parser import parse


def entry_point(argv):
    definitions = Definitions()
    # print(definitions.get_definition("$Context"))
    print(parse("1+1 (*1+2*)", definitions))
    # print(parse("1 + 2 + \:0030"))
    print(parse("\\[Theta]", definitions))
    # while True:
    #     x = raw_input(">> ")
    #     print(parse(x, definitions))
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
