# from __future__ import unicode_literals
import sys

try:
    import rpython
except ImportError:
    rpython = None

from rmathics.expression import Expression, Symbol, String, Integer, Rational
from rmathics.definitions import Definitions
from rmathics.parser import parse
from rmathics.evaluation import evaluate

def entry_point(argv):
    definitions = Definitions()
    # print(definitions.get_definition("$Context"))
    # print(parse("1 + 2 3", definitions))
    # print(parse("1 + 2 + \:0030"))
    # print(parse("\\[Theta]", definitions))
    assert Expression(Symbol('Sin'), Integer(1)).eq(Expression(Symbol('Sin'), Integer(1)))
    assert Rational.from_float(0.5).to_float() == 0.5

    # definitions.set_attributes('Global`f', ['Flat'])
    # # expr = Expression(Symbol('Global`f'), Expression(Symbol('Global`f'), Integer(1), Integer(2)), Integer(3), Integer(4))
    # expr, messages = parse('Global`f[1, Global`f[2, Global`f[3]], Global`f[4], 5]', definitions)
    # result, message = evaluate(expr, definitions)
    # print result.repr()
    # if result == Expression(Symbol('Global`f'), Integer(1), Integer(2), Integer(3), Integer(4)):
    #     print "equal"

    definitions.set_attributes('Global`g', ['Listable'])
    expr, messages = parse('Global`g[{a,b,c}, x]', definitions)
    result, message = evaluate(expr, definitions)

    print result.repr()

    if not rpython:
        while True:
            x = raw_input(">> ")
            expr, messages = parse(x, definitions)
            for message in messages:
                print(message)
            result, messages = evaluate(expr, definitions)
            for message in messages:
                print(message)
            print(result.repr())
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
