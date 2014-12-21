import sys
from rmathics.expression import Expression, Symbol, String
from rmathics.definition import Definitions
from rmathics.parser import parse


def entry_point(argv):
    a = Expression("Length", String("abc"))
    print(a.format())

    definitions = Definitions()
    # print(definitions.get_definition("$Context"))
    # print(parse(u"1+1 (*1+2*)"))
    # print(parse(u"1 + 2 + \:0030"))
    print(parse(u"\\[Theta]"))
    while True:
        x = raw_input(">> ")
        print(parse(x).format())
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
