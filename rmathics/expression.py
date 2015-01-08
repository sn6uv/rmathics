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
    c_mpz_cmp,
    MPQ_STRUCT, c_mpq_init, c_mpq_clear, c_mpq_equal, c_mpq_get_str,
    c_mpq_get_num, c_mpq_get_den, c_mpq_get_d,
    MPF_STRUCT, MP_EXP_TP, c_mpf_init2, c_mpf_clear, c_mpf_get_str,
    c_mpf_get_d, c_mpf_eq,
)

from math import log
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
    def __init__(self, prec):
        self.prec = prec
        self.value = lltype.malloc(MPF_STRUCT, flavor='raw')
        c_mpf_init2(self.value, rffi.r_ulong(prec))

    def __clear__(self):
        c_mpf_clear(self.value)
        lltype.free(self.value, flavor='raw')

    def to_str(self, base=10):
        assert 2 <= base <= 62
        exp = lltype.malloc(MP_EXP_TP.TO, flavor='raw')
        n = int(self.prec * log(2) / log(10))
        l = n + 2
        p = lltype.malloc(rffi.CCHARP.TO, l, flavor='raw')
        c_mpf_get_str(p, exp, rffi.r_int(base), rffi.r_size_t(n), self.value)
        result = rffi.charp2str(p)
        lltype.free(p, flavor='raw')
        lltype.free(exp, flavor='raw')
        # TODO format result
        return result

    def to_float(self):
        return c_mpf_get_d(self.value)

    def same(self, other):
        if not isinstance(other, Real):
            return False
        # Approximate numbers with machine precision or higher are considered
        # equal if they differ in at most their last seven binary digits
        prec = min(self.prec, other.prec) - 7
        # TODO:
        # For numbers below machine precision the required tolerance is reduced
        # in proportion to the precision of the numbers.
        return c_mpf_eq(self.value, other.value, rffi.r_ulong(prec)) != 0


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
    def __init__(self):
        Number.__init__(self)
        self.value = lltype.malloc(MPQ_STRUCT, flavor='raw')
        c_mpq_init(self.value)

    def __del__(self):
        c_mpq_clear(self.value)
        lltype.free(self.value, flavor='raw')

    def same(self, other):
        return (isinstance(other, Rational) and
                c_mpq_equal(self.value, other.value) != 0)

    def to_str(self, base=10):
        assert 2 <= base <= 62

        # find the required length
        num = lltype.malloc(MPZ_STRUCT, flavor='raw')
        den = lltype.malloc(MPZ_STRUCT, flavor='raw')
        c_mpq_get_num(num, self.value)
        c_mpq_get_den(den, self.value)
        l = (c_mpz_sizeinbase(num, rffi.r_int(base)) +
             c_mpz_sizeinbase(den, rffi.r_int(base)) + 3)
        lltype.free(num, flavor='raw')
        lltype.free(den, flavor='raw')

        # get the str
        p = lltype.malloc(rffi.CCHARP.TO, l, flavor='raw')
        c_mpq_get_str(p, base, self.value)
        result = rffi.charp2str(p)
        lltype.free(p, flavor='raw')
        return result

    def to_float(self):
        return c_mpq_get_d(self.value)

    def repr(self):
        return self.to_str()


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
