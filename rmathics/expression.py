class BaseExpression(object):
    def __init__(self, *args):
        pass

    def get_precision(self):
        return None

    def evaluate(self, evaluation):
        # raise NotImplementedError
        pass

    def get_head(self):
        return None

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


class Expression(BaseExpression):
    def __init__(self, head, *leaves):
        assert isinstance(head, str)
        # assert all(isinstance(leaf, BaseExpression) for leaf in leaves)
        self.head = Symbol(head)
        self.leaves = leaves

    def get_head(self):
        return self.head

    def format(self, format="FullForm"):
        return "%s[%s]" % (
            self.head.format(),
            ", ".join([leaf.format() for leaf in self.leaves]))


class Atom(BaseExpression):
    def is_atom(self):
        return True

    def get_head(self):
        return Symbol(self.__class__.__name__)


class String(Atom):
    def __init__(self, value):
        Atom.__init__(self)
        assert isinstance(value, str)
        self.value = value

    def format(self, format="FullForm"):
        return '"%s"' % self.value

    def is_string(self):
        return True


class Symbol(Atom):
    def __init__(self, name):
        Atom.__init__(self)
        assert isinstance(name, str)
        self.name = name

    def format(self, format="FullForm"):
        return self.name

    def is_symbol(self):
        return True


class Number(Atom):
    def is_number(self):
        return True


class Integer(Number):
    def __init__(self, value):
        # assert isinstance(value, mpz)
        self.value = value
        Number.__init__(self)


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
