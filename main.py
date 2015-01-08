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
    z = str2Real('0.34123e41', 60)
    print z.to_float()
    print z.to_str()
    print str2Real('1.34123e5', 60).to_str()
    print str2Real('1.34123e6', 60).to_str()
    print str2Real('1.34123e-5', 60).to_str()
    print str2Real('1.34123e-6', 60).to_str()
    print str2Real('1.34123', 60).to_str()
    print str2Real('0.134123', 60).to_str()
    print str2Real('0.0134123', 60).to_str()

    x = str2Real('0.5', 60)
    y = str2Real('0.5', 60)
    z = str2Real('0.7', 60)
    assert x.same(y)
    assert not x.same(z)

    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
