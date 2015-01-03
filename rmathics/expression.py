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
import sys

from rply.token import BaseBox
from rmathics.rpython_util import zip, all
from rmathics.gmp import gmp, ffi


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

    def ne(self, other):
        return not self.eq(other)

    def eq(self, other):
        return False

    def to_str(self):
        raise TypeError("method only valid for String instances")

    def to_int(self):
        raise TypeError("method only valid for Integer instances")


class Expression(BaseExpression):
    def __init__(self, head, *leaves):
        BaseExpression.__init__(self)
        assert isinstance(head, BaseExpression)
        assert all([isinstance(leaf, BaseExpression) for leaf in list(leaves)])
        self.head = head
        self.leaves = list(leaves)

    def repr(self):
        return "%s[%s]" % (
            self.head.repr(), ", ".join([leaf.repr() for leaf in self.leaves]))

    def eq(self, other):
        if not isinstance(other, Expression):
            return False
        if not self.head.eq(other.head):
            return False
        if len(self.leaves) != len(other.leaves):
            return False
        for self_leaf, other_leaf in zip(self.leaves, other.leaves):
            if not self_leaf.eq(other_leaf):
                return False
        return True


class Atom(BaseExpression):
    def __init__(self):
        BaseExpression.__init__(self)
        self.head = Symbol('System`%s' % self.__class__.__name__)
        self.leaves = []

    def is_atom(self):
        return True


class String(Atom):
    def __init__(self, value):
        Atom.__init__(self)
        assert isinstance(value, str)
        self.value = value

    def repr(self):
        return '"%s"' % self.value

    def is_string(self):
        return True

    def eq(self, other):
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

    def repr(self):
        return self.name

    def is_symbol(self):
        return True

    def get_name(self):
        return self.name

    def eq(self, other):
        return (isinstance(other, Symbol) and
                self.get_name() == other.get_name())


class Number(Atom):
    def is_number(self):
        return True


class Integer(Number):
    def __init__(self, value):
        assert isinstance(value, int)
        Number.__init__(self)
        self.value = ffi.new('mpz_t')
        gmp.mpz_init_set_si(self.value, value)

    def __del__(self):
        gmp.mpz_clear(self.value)

    @classmethod
    def from_mpz(cls, value):
        self = object.__new__(cls)
        Number.__init__(self)
        self.value = value
        return self

    @classmethod
    def from_str(cls, value, base=10):
        self = object.__new__(cls)
        Number.__init__(self)
        self.value = ffi.new('mpz_t')
        retcode = gmp.mpz_init_set_str(self.value, value, base)
        assert retcode == 0
        return self

    def to_int(self):
        if gmp.mpz_fits_slong_p(self.value):
            return gmp.mpz_get_si(self.value)
        else:
            raise OverflowError

    def repr(self):
        return str(self.value)

    def eq(self, other):
        return isinstance(other, Integer) and gmp.mpz_cmp(self.value, other.value) == 0


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


def strip_context(name):
    if '`' in name:
        return name[name.rindex('`') + 1:]
    return name
