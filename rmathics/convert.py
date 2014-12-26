def str_to_mpz(value):
    assert isinstance(value, str)
    pass


def str_to_mpfr(value):
    assert isinstance(value, str)
    pass


def str_to_mpc(value):
    assert isinstance(value, str)
    pass


def str_to_mpq(value):
    assert isinstance(value, str)
    pass


def float_to_mpfr(value):
    assert isinstance(value, float)
    pass


def complex_to_mpc(value):
    assert isinstance(value, value)
    pass


def int_to_mpz(value):
    assert isinstance(value, (int, long))
    pass


def ints_to_mpq(num, den):
    assert isinstance(num, (int, long))
    assert isinstance(den, (int, long))
    pass


def str_to_num(value):
    return int(value)
