import sys

from rmathics.convert import int2Integer, str2Integer, int2Rational, float2Rational, float2Real
from rmathics.expression import Real


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
    x = int2Rational(2, 4)
    assert x.same(y)
    print x.to_str()
    print x.to_float()

    x = Real(53)
    y = float2Real(0.543214, 53)
    print(y.to_str())

    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
