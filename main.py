import sys

from rmathics.convert import int2Integer, str2Integer, int2Rational, str2Rational, float2Rational, str2Real, float2Real
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
    z = str2Rational('24/48')
    assert x.same(z)
    print x.to_str()
    print x.to_float()
    print z.to_float()

    x = Real(53)
    y = float2Real(0.543214, 53)
    print(y.to_float())
    z = str2Real('-0.34123e41', 60)
    print z.to_float()

    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
