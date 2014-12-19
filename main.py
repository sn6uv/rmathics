import sys
from rmathics.expression import Expression, Symbol, String
from rmathics.definition import Definitions


def entry_point(argv):
    a = Expression(Symbol("Length"), String("abc"))
    print(a.format())

    definitions = Definitions()
    print(definitions.get_definition("$Context"))
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
