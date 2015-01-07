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
from rmathics.rpython_util import zip, all
from rmathics.gmp import (
    MPZ_STRUCT, c_mpz_init, c_mpz_clear, c_mpz_sizeinbase, c_mpz_get_str,
    c_mpz_cmp
)

from rpython.rtyper.lltypesystem import rffi, lltype


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

    def same(self, other):
        return False

    def to_str(self):
        raise NotImplementedError

    def to_int(self):
        raise NotImplementedError


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

    def same(self, other):
        if not isinstance(other, Expression):
            return False
        if not self.head.same(other.head):
            return False
        if len(self.leaves) != len(other.leaves):
            return False
        for self_leaf, other_leaf in zip(self.leaves, other.leaves):
            if not self_leaf.same(other_leaf):
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

    def same(self, other):
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

    def same(self, other):
        return (isinstance(other, Symbol) and
                self.get_name() == other.get_name())


class Number(Atom):
    def is_number(self):
        return True


class Integer(Number):
    def __init__(self):
        Number.__init__(self)
        self.value = lltype.malloc(MPZ_STRUCT, flavor='raw')
        c_mpz_init(self.value)

    def __del__(self):
        c_mpz_clear(self.value)
        lltype.free(self.value, flavor='raw')

    def to_str(self, base=10):
        assert 2 <= base <= 62
        l = c_mpz_sizeinbase(self.value, rffi.r_int(base)) + 2
        p = lltype.malloc(rffi.CCHARP.TO, l, flavor='raw')
        c_mpz_get_str(p, rffi.r_int(base), self.value)
        result = rffi.charp2str(p)
        lltype.free(p, flavor='raw')
        return result

    def repr(self):
        return self.to_str()

    def same(self, other):
        return (isinstance(other, Integer) and
                c_mpz_cmp(self.value, other.value) == 0)


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
    def __init__(self, num, den):
        pass
        # assert isinstance(num, int) and isinstance(den, int)
        # if den < 0:
        #     num, den = -1 * num, -1 * den
        # Number.__init__(self)
        # self.value = ffi.new('mpq_t')
        # gmp.mpq_init(self.value)
        # gmp.mpq_set_si(self.value, num, den)
        # gmp.mpq_canonicalize(self.value)

    # @classmethod
    # def from_float(cls, value):
    #     assert isinstance(value, float)
    #     self = object.__new__(cls)
    #     Number.__init__(self)
    #     self.value = ffi.new('mpq_t')
    #     gmp.mpq_init(self.value)
    #     gmp.mpq_set_d(self.value, value)
    #     return self

    # def to_float(self):
    #     return gmp.mpq_get_d(self.value)

    # @classmethod
    # def from_str(cls, value, base=10):
    #     assert isinstance(value, str)
    #     self = object.__new__(cls)
    #     Number.__init__(self)
    #     self.value = ffi.new('mpq_t')
    #     gmp.mpq_init(self.value)
    #     retcode = gmp.mpq_set_str(self.value, value, base)
    #     assert retcode == 0
    #     gmp.mpq_canonicalize(self.value)
    #     return self

    # def to_str(self, base=10):
    #     assert 2 <= base <= 62
    #     l = (gmp.mpz_sizeinbase(gmp.mpq_numref(self.value), base) +
    #          gmp.mpz_sizeinbase(gmp.mpq_denref(self.value), base) + 3)
    #     p = ffi.new('char[]', l)
    #     gmp.mpq_get_str(p, base, self.value)
    #     return ffi.string(p)

    # @classmethod
    # def from_ints(cls, num, den):
    #     assert isinstance(num, int) and isinstance(den, int)
    #     if den < 0:
    #         num, den = -1 * num, -1 * den
    #     self = object.__new__(cls)
    #     Number.__init__(self)
    #     self.value = ffi.new('mpq_t')
    #     gmp.mpq_init(self.value)
    #     gmp.mpq_set_si(self.value, num, den)
    #     gmp.mpq_canonicalize(self.value)
    #     return self

    # def num(self):
    #     return Integer.from_mpz(gmp.mpq_numref(self.value))

    # def den(self):
    #     return Integer.from_mpz(gmp.mpq_numref(self.value))

    # def to_ints(self):
    #     return self.num(), self.den()

    # def repr(self):
    #     return self.to_str()

    # def __del__(self):
    #     gmp.mpq_clear(self.value)

    # def same(self, other):
    #     return (isinstance(other, Rational) and
    #             gmp.mpq_equal(self.value, other.value) != 0)


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
