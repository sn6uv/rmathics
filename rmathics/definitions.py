# from __future__ import unicode_literals

from rmathics.expression import (
    BaseExpression, Expression, Symbol, String, fully_qualified_symbol_name,
    Integer, Rational, Real,
)
from rmathics.rpython_util import all
from rmathics.convert import int2Integer, int2Rational, float2Real
from rmathics.gmp import c_mpz_add, c_mpq_add, c_mpf_add, c_mpq_set_z, c_mpf_set_z, c_mpf_set_q

known_attributes = (
    'Orderless', 'Flat', 'OneIdentity', 'Listable', 'Constant',
    'NumericFunction', 'Protected', 'Locked', 'ReadProtected', 'HoldFirst',
    'HoldRest', 'HoldAll', 'HoldAllComplete', 'NHoldFirst', 'NHoldRest',
    'NHoldAll', 'SequenceHold', 'Temporary', 'Stub')


class Definitions(object):
    """
    Symbol table of definitions (to be filled with Definition instances)
    """
    def __init__(self):
        self.table = {}

        self.add_definition('System`$Context', Definition())
        self.add_definition('System`$ContextPath', Definition())
        self.set_context('Global`')
        self.set_context_path(['System`', 'Global'])
        # FIXME
        self.set_attributes('System`Plus', ['Orderless'])

    def get_context(self):
        """
        return current $Context as a str
        """
        context = self.get_ownvalues('System`$Context')
        assert isinstance(context, String)
        return context.to_str()

    def get_context_path(self):
        """
        return current $ContextPath as a list of str
        """
        path = self.get_ownvalues('System`$ContextPath')
        assert isinstance(path, Expression)
        assert path.head.same(Symbol('System`List'))
        return [leaf.to_str() for leaf in path.leaves]

    def set_context(self, context):
        """
        set $Context given a str
        """
        assert isinstance(context, str)
        ownvalues = String(context)
        self.set_ownvalues('System`$Context', ownvalues)

    def set_context_path(self, context_path):
        """
        set $ContextPath given a list of str
        """
        assert isinstance(context_path, list)
        assert all([isinstance(c, str) for c in context_path])
        ownvalues = Expression(Symbol('System`List'))
        ownvalues.leaves = [String(c) for c in context_path]
        self.set_ownvalues('System`$ContextPath', ownvalues)

    def get_accessible_contexts(self):
        "Return the contexts reachable though $Context or $ContextPath."
        accessible_ctxts = set(self.get_context_path())
        accessible_ctxts.add(self.get_context())
        return accessible_ctxts

    def lookup_name(self, name):
        """
        Determine the full name (including context) for a symbol name.

        - If the name begins with a context mark, it's in the context
          given by $Context.
        - Otherwise, if it contains a context mark, it's already fully
          specified.
        - Otherwise, it doesn't contain a context mark: try $Context,
          then each element of $ContextPath, taking the first existing
          symbol.
        - Otherwise, it's a new symbol in $Context.
        """

        assert isinstance(name, str)

        # Bail out if the name we're being asked to look up is already
        # fully qualified.
        if fully_qualified_symbol_name(name):
            return name

        current_context = self.get_context()

        if '`' in name:
            if name.startswith('`'):
                return current_context + name.lstrip('`')
            return name

        with_context = current_context + name
        if not (with_context in self.table):
            for ctx in self.get_context_path():
                n = ctx + name
                if n in self.table:
                    return n
        return with_context

    def get_definition(self, name):
        """
        Return the definition if it exists or create it if it doesn't
        """
        name = self.lookup_name(name)
        defn = self.table.get(name, None)
        if defn is None:
            defn = Definition()
            self.table[name] = defn
        return defn

    def get_ownvalues(self, name):
        assert isinstance(name, str)
        ownvalues = self.get_definition(name).ownvalues
        assert ownvalues.head.same(Symbol('System`List'))
        assert len(ownvalues.leaves) == 1
        head, leaves = ownvalues.leaves[0].head, ownvalues.leaves[0].leaves
        # assert head is rule
        assert len(leaves) == 2
        return leaves[1]

    def set_ownvalues(self, name, ownvalues):
        assert isinstance(name, str) and isinstance(ownvalues, BaseExpression)
        name = self.lookup_name(name)
        defn = self.get_definition(name)
        defn.ownvalues = Expression(
            Symbol('System`List'),
            Expression(
                Symbol('System`RuleDelayed'),
                Expression(Symbol('System`HoldPattern'), Symbol(name)),
                ownvalues))

    def reset_definition(self, name):
        assert isinstance(name, str)
        del self.table[self.lookup_name(name)]

    def add_definition(self, name, definition):
        assert isinstance(name, str)
        self.table[self.lookup_name(name)] = definition

    def get_attributes(self, name):
        assert isinstance(name, str)
        attributes = self.get_definition(name).attributes
        assert attributes.head.same(Symbol('System`List'))
        assert all([leaf.get_name().startswith('System`')
                    for leaf in attributes.leaves])
        return [leaf.get_name()[7:] for leaf in attributes.leaves]

    def set_attributes(self, name, attributes):
        assert isinstance(name, str)
        assert isinstance(attributes, list)
        assert all([isinstance(attr, str) and attr in known_attributes
                    for attr in attributes])
        name = self.lookup_name(name)
        defn = self.get_definition(name)
        defn.attributes = Expression(Symbol('System`List'))
        defn.attributes.leaves = [Symbol('System`' + attribute)
                                  for attribute in attributes]

    def get_messages(self, name):
        assert isinstance(name, str)
        messages = self.get_definition(name).messages
        assert messages.head.same(Symbol('System`List'))
        messages = messages.leaves
        assert all([message.leaves[0].head.same(Symbol('HoldPattern'))
                    for message in messages])
        assert all([isinstance(message.leaves[1], String)
                    for message in messages])
        return {message.leaves[0].leaves[0].leaves[1].to_str():
                message.leaves[1].to_str() for message in messages}

    def construct_message(self, *message):
        assert len(message) >= 2
        message_base = message[0] + '::' + message[1] + ': '
        messages = self.get_messages(message[0])
        message_text = messages.get(message[1], '-- Message text not found --')
        # TODO format message_text with remaining components of message
        return message_base + message_text


class Definition(object):
    """
    Individual definition entry (to be stored in Definitions)
    """
    def __init__(self,
                 rules=Expression(Symbol('System`List')),
                 ownvalues=Expression(Symbol('System`List')),
                 downvalues=Expression(Symbol('System`List')),
                 subvalues=Expression(Symbol('System`List')),
                 upvalues=Expression(Symbol('System`List')),
                 formatvalues=Expression(Symbol('System`List')),
                 messages=Expression(Symbol('System`List')),
                 attributes=Expression(Symbol('System`List')),
                 options=Expression(Symbol('System`List')),
                 nvalues=Expression(Symbol('System`List')),
                 defaultvalues=Expression(Symbol('System`List'))):
        self.rules = rules
        self.ownvalues = ownvalues
        self.downvalues = downvalues
        self.subvalues = subvalues
        self.upvalues = upvalues
        self.formatvalues = formatvalues
        self.messages = messages
        self.attributes = attributes
        self.options = options
        self.nvalues = nvalues
        self.defaultvalues = defaultvalues

    def __repr__(self):
        s = (
            '<Definition: name: %s, '
            'downvalues: %s, formats: %s, attributes: %s>') % (
                self.downvalues, self.formatvalues, self.attributes)
        return s.encode('unicode_escape')

builtins = []
def builtin(patt):
    assert isinstance(patt, BaseExpression)
    def wrapper(func):
        builtins.append((patt, func))
        return func
    return wrapper


@builtin(Expression(Symbol('System`Plus'),
    Expression(Symbol('System`Pattern'), Symbol('x0'), Expression(Symbol('System`BlankNullSequence'), Symbol('System`Integer'))),
    Expression(Symbol('System`Pattern'), Symbol('x1'), Expression(Symbol('System`BlankNullSequence'), Symbol('System`Rational'))),
    Expression(Symbol('System`Pattern'), Symbol('x2'), Expression(Symbol('System`BlankNullSequence'), Symbol('System`Real'))),
))
def plus(mappings):
    ints = mappings['x0']
    rats = mappings['x1']
    reals = mappings['x2']

    assert ints.head.same(Symbol('System`Sequence'))
    assert rats.head.same(Symbol('System`Sequence'))
    assert reals.head.same(Symbol('System`Sequence'))

    ints = ints.leaves
    rats = rats.leaves
    reals = reals.leaves

    # most of the asserts here are for the RPython annotator
    result = None
    if ints:
        result = int2Integer(0)
        assert isinstance(result, Integer)
        value = result.value
        for arg in ints:
            assert isinstance(arg, Integer)
            c_mpz_add(value, value, arg.value)

    if rats:
        if result is None:
            result = int2Rational(0, 1)
        else:
            intresult = result
            result = Rational()
            c_mpq_set_z(result.value, intresult.value)
        assert isinstance(result, Rational)
        value = result.value
        for arg in rats:
            assert isinstance(arg, Rational)
            c_mpq_add(value, value, arg.value)

    if reals:
        # minimum precision
        prec = 0
        for arg in reals:
            assert isinstance(arg, Real)
            if arg.prec < prec:
                prec = arg.prec

        if result is None:
            result = float2Real(0.0, prec)
        elif isinstance(result, Integer):
            intresult = result
            result = Real(prec)
            c_mpf_set_z(result.value, intresult.value)
        elif isinstance(result, Rational):
            ratresult = result
            result = Real(prec)
            c_mpf_set_q(result.value, ratresult.value)
        assert isinstance(result, Real)
        value = result.value
        for arg in reals:
            assert isinstance(arg, Real)
            c_mpf_add(value, value, arg.value)

    assert result is not None
    return result
