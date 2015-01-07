import sys

from rmathics.expression import int2Integer, str2Integer


try:
    input = raw_input
except NameError:
    pass


def entry_point(argv):
    x = int2Integer(10)
    y = str2Integer('10')
    print(x.same(y))
    print(x.to_str())
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
