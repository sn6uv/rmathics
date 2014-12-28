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

from rply.token import BaseBox


class BaseExpression(BaseBox):
    def __init__(self, *args):
        self.parenthesized = False

    def get_precision(self):
        return None

    def evaluate(self, evaluation):
        pass

    def is_atom(self):
        return False

    def is_string(self):
        return False

    def is_symbol(self):
        return False

    def is_number(self):
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        return False

    def getstr(self):
        raise TypeError("method only valid for String instances")

    def getint(self):
        raise TypeError("method only valid for Integer instances")


class Expression(BaseExpression):
    def __init__(self, head, *leaves):
        BaseExpression.__init__(self)
        assert isinstance(head, BaseExpression)
        # assert all(isinstance(leaf, BaseExpression) for leaf in leaves)
        self.head = head
        self.leaves = list(leaves)

    def __repr__(self):
        return "%s[%s]" % (
            self.head, ", ".join(["%s" % leaf for leaf in self.leaves]))

    def __eq__(self, other):
        if not isinstance(other, Expression):
            return False
        if self.head != other.head:
            return False
        if len(self.leaves) != len(other.leaves):
            return False
        for self_leaf, other_leaf in zip(self.leaves, other.leaves):
            if self_leaf != other_leaf:
                return False
        return True


class Atom(BaseExpression):
    def __init__(self):
        BaseExpression.__init__(self)
        self.head = Symbol(ensure_context(str(self.__class__.__name__)))
        self.leaves = []

    def is_atom(self):
        return True


class String(Atom):
    def __init__(self, value):
        Atom.__init__(self)
        assert isinstance(value, str)
        self.value = value

    def __repr__(self):
        return '"%s"' % self.value

    def is_string(self):
        return True

    def __eq__(self, other):
        return isinstance(other, String) and self.value == other.value

    def to_str(self):
        return self.value

class Symbol(Atom):
    def __init__(self, name):
        assert isinstance(name, str)
        if name == 'System`Symbol':     # prevent recursion at the root symbol
            BaseExpression.__init__(self)
            self.head = self
            self.leaves = []
        else:
            Atom.__init__(self)
        self.name = name

    def __repr__(self):
        return self.name

    def is_symbol(self):
        return True

    def get_name(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, Symbol) and self.name == other.name


class Number(Atom):
    def is_number(self):
        return True


class Integer(Number):
    def __init__(self, value):
        # assert isinstance(value, mpz)
        Number.__init__(self)
        self.value = value

    @classmethod
    def from_int(cls, value):
        assert isinstance(value, int)
        pass

    def to_int(self):
        pass

    def __repr__(self):
        return "%i" % self.value

    def __eq__(self, other):
        return isinstance(other, Integer) and self.value == other.value

    def getint(self):
        return self.value


class Real(Number):
    def __init__(self, value):
        # assert isinstance(value, mpfr)
        Number.__init__(self)
        self.value = value

    @classmethod
    def from_float(cls, value):
        assert isinstance(value, float)
        pass

    @classmethod
    def from_int(cls, value):
        assert isinstance(value, int)
        pass

    def to_float(self):
        pass


class Complex(Number):
    def __init__(self, value):
        # assert isinstance(value, mpc)
        Number.__init__(self)
        self.value = value

    @classmethod
    def from_complex(cls, value):
        assert isinstance(value, complex)
        pass

    @classmethod
    def from_float(cls, value):
        assert isinstance(value, float)
        pass

    @classmethod
    def from_int(cls, value):
        assert isinstance(value, int)
        pass

    def to_complex(self):
        pass


class Rational(Number):
    def __init__(self, value):
        # assert isinstance(value, mpq)
        Number.__init__(self)
        self.value = value

    @classmethod
    def from_float(cls, value):
        assert isinstance(value, float)
        pass

    @classmethod
    def from_ints(cls, num, den):
        assert isinstance(value, num) and isinstance(value, den)
        pass

    def to_ints(self):
        pass


def fully_qualified_symbol_name(name):
    return (isinstance(name, str) and
            '`' in name and
            not name.startswith('`') and
            not name.endswith('`') and
            '``' not in name)


def valid_context_name(ctx, allow_initial_backquote=False):
    return (isinstance(ctx, str) and
            ctx.endswith('`') and
            '``' not in ctx and
            (allow_initial_backquote or not ctx.startswith('`')))


def ensure_context(name):
    assert isinstance(name, str)
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
