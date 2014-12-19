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
        self.head = head
        # assert isinstance(head, Symbol)
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
        # assert isinstance(value, basestring)
        self.value = value

    def format(self, format="FullForm"):
        return '"%s"' % self.value

    def is_string(self):
        return True


class Symbol(Atom):
    def __init__(self, name):
        Atom.__init__(self)
        # assert isinstance(name, basestring)
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
        # TODO
        self.value = value
        Number.__init__(self)


class Real(Number):
    def __init__(self, value):
        # TODO
        self.value = value
        Number.__init__(self)


class Complex(Number):
    def __init__(self, value):
        # TODO
        self.value = value
        Number.__init__(self)


class Rational(Number):
    def __init__(self, value):
        # TODO
        self.value = value
        Number.__init__(self)
