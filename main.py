import sys
from expression import Expression, Symbol, String


def entry_point(argv):
    a = Expression(Symbol("Length"), String("abc"))
    print(a.format())
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
