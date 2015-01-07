import sys

from rmathics.convert import int2Integer, str2Integer, int2Rational, float2Rational


try:
    input = raw_input
except NameError:
    pass


def entry_point(argv):
    x = int2Integer(10)
    y = str2Integer('10')
    assert x.same(y)

    x = int2Rational(1, 2)
    y = float2Rational(0.5)
    assert x.same(y)

    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
