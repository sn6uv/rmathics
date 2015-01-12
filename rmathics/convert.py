from rpython.rtyper.lltypesystem import rffi

from rmathics import Integer, Rational, Real
from rmathics.gmp import (
    c_mpz_set_si, c_mpz_set_str, c_mpz_ui_pow_ui, c_mpz_mul,
    c_mpq_set_si, c_mpq_set_str, c_mpq_set_d, c_mpq_canonicalize,
    c_mpf_set_str, c_mpf_set_d,
)


def int2Integer(value):
    assert isinstance(value, int)
    result = Integer()
    c_mpz_set_si(result.value, rffi.r_long(value))
    return result


def str2Integer(value, base=10):
    assert isinstance(value, str)
    assert 2 <= base <= 62
    result = Integer()
    p = rffi.str2charp(value)
    retcode = c_mpz_set_str(result.value, p, rffi.r_int(base))
    assert retcode == 0
    rffi.free_charp(p)
    return result


def int2Rational(num, den):
    assert isinstance(num, int)
    assert isinstance(den, int)
    if den < 0:
        # expects den to be an unsigned long int
        num, den = (-1) * num, (-1) * den
    result = Rational()
    c_mpq_set_si(result.value, rffi.r_long(num), rffi.r_ulong(den))
    c_mpq_canonicalize(result.value)
    return result


def str2Rational(value, base=10):
    assert isinstance(value, str)
    assert 2 <= base <= 62
    result = Rational()
    p = rffi.str2charp(value)
    retcode = c_mpq_set_str(result.value, p, rffi.r_int(base))
    assert retcode == 0
    c_mpq_canonicalize(result.value)
    rffi.free_charp(p)
    return result


def float2Rational(value):
    assert isinstance(value, float)
    result = Rational()
    c_mpq_set_d(result.value, value)
    c_mpq_canonicalize(result.value)
    return result


def str2Real(value, prec, base=10):
    assert isinstance(value, str)
    assert 2 <= base <= 62
    result = Real(prec)
    p = rffi.str2charp(value)
    # we pass negative base so that the exponent is intepreted as decimal
    retcode = c_mpf_set_str(result.value, p, rffi.r_int(-base))
    assert retcode == 0
    rffi.free_charp(p)
    return result


def float2Real(value, prec):
    result = Real(prec)
    c_mpf_set_d(result.value, value)
    return result


def _mul_pow(value, base, exp):
    """
    Multiplies a given mpz by base^exp
    """
    factor = Integer()
    c_mpz_ui_pow_ui(factor.value, base, exp)
    c_mpz_mul(value, value, factor.value)
