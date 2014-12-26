"""
The structure of things:

- BaseExpression
  - Expression
  - Atom
    - String
    - Symbol
    - Number
      - Integer
      - Rational
      - Real
      - Complex
"""

from __future__ import unicode_literals


class BaseExpression(object):
    def __init__(self, *args):
        self.parenthesized = False

    def get_precision(self):
        return None

    def evaluate(self, evaluation):
        pass

    def format(self, format="FullForm"):
        return None

    def is_atom(self):
        return False

    def is_string(self):
        return False

    def is_symbol(self):
        return False

    def is_number(self):
        return False

    def same(self, other):
        pass


class Expression(BaseExpression):
    def __init__(self, head, *leaves):
        assert isinstance(head, BaseExpression)
        # assert all(isinstance(leaf, BaseExpression) for leaf in leaves)
        self.head = head
        self.leaves = list(leaves)

    def format(self, format="FullForm"):
        return "%s[%s]" % (
            self.head.format(),
            ", ".join([leaf.format() for leaf in self.leaves]))

    def same(self, other):
        if not isinstance(other, Expression):
            return False
        if self.head.same(other.head):
            return False
        if not self.head.same(other.head):
            return False
        if len(self.leaves) != len(other.leaves):
            return False
        for leaf, other in zip(self.leaves, other.leaves):
            if not leaf.same(other):
                return False
        return True


class Atom(BaseExpression):
    def __init__(self):
        self.head = Symbol(ensure_context(self.__class__.__name__))

    def is_atom(self):
        return True


class String(Atom):
    def __init__(self, value):
        Atom.__init__(self)
        assert isinstance(value, basestring)
        self.value = value

    def format(self, format="FullForm"):
        return '"%s"' % self.value

    def is_string(self):
        return True

    def same(self, other):
        return isinstance(other, String) and self.value == other.value


class Symbol(Atom):
    def __init__(self, name):
        if name == 'System`Symbol':     # prevent recursion at the root symbol
            self.head = self
        else:
            Atom.__init__(self)
        assert isinstance(name, basestring)
        self.name = name

    def format(self, format="FullForm"):
        return self.name

    def is_symbol(self):
        return True

    def get_name(self):
        return self.name

    def same(self, other):
        return isinstance(other, Symbol) and self.name == other.name


class Number(Atom):
    def is_number(self):
        return True


class Integer(Number):
    def __init__(self, value):
        # assert isinstance(value, mpz)
        self.value = value
        Number.__init__(self)

    def format(self, format="FullForm"):
        return "%i" % self.value

    def same(self, other):
        return isinstance(other, Integer) and self.value == other.value


class Real(Number):
    def __init__(self, value):
        Number.__init__(self)
        # assert isinstance(value, mpfr)
        self.value = value


class Complex(Number):
    def __init__(self, value):
        Number.__init__(self)
        # assert isinstance(value, mpc)
        self.value = value


class Rational(Number):
    def __init__(self, value):
        Number.__init__(self)
        # assert isinstance(value, mpq)
        self.value = value


def fully_qualified_symbol_name(name):
    return (isinstance(name, basestring)
            and '`' in name
            and not name.startswith('`')
            and not name.endswith('`')
            and '``' not in name)


def valid_context_name(ctx, allow_initial_backquote=False):
    return (isinstance(ctx, basestring)
            and ctx.endswith('`')
            and '``' not in ctx
            and (allow_initial_backquote or not ctx.startswith('`')))


def ensure_context(name):
    assert isinstance(name, basestring)
    assert name != ''
    if '`' in name:
        # Symbol has a context mark -> it came from the parser
        assert fully_qualified_symbol_name(name)
        return name
    # Symbol came from Python code doing something like
    # Expression('Plus', ...) -> use System`
    return 'System`' + name


def strip_context(name):
    if '`' in name:
        return name[name.rindex('`') + 1:]
    return name


# system_symbols('A', 'B', ...) -> ['System`A', 'System`B', ...]
def system_symbols(*symbols):
    return [ensure_context(s) for s in symbols]


# system_symbols_dict({'SomeSymbol': ...}) -> {'System`SomeSymbol': ...}
def system_symbols_dict(d):
    return dict(((ensure_context(k), v) for k, v in d.iteritems()))
