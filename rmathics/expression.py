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

    def get_head_name(self):
        return self.get_head().get_name()

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
        assert isinstance(head, BaseExpression)
        # assert all(isinstance(leaf, BaseExpression) for leaf in leaves)
        self.head = head
        self.leaves = list(leaves)

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
        assert isinstance(value, basestring)
        self.value = value

    def format(self, format="FullForm"):
        return '"%s"' % self.value

    def is_string(self):
        return True


class Symbol(Atom):
    def __init__(self, name):
        Atom.__init__(self)
        assert isinstance(name, basestring)
        self.name = name

    def format(self, format="FullForm"):
        return self.name

    def is_symbol(self):
        return True

    def get_name(self):
        return self.name


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
