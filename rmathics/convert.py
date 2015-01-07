from rpython.rtyper.lltypesystem import rffi

from rmathics import Integer
from rmathics.gmp import c_mpz_set_si, c_mpz_set_str


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
