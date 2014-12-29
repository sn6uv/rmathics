# from __future__ import unicode_literals

from rmathics.expression import (
    BaseExpression, Expression, Symbol, String, ensure_context,
    fully_qualified_symbol_name)

known_attributes = set([
    'Orderless', 'Flat', 'OneIdentity', 'Listable', 'Constant',
    'NumericFunction', 'Protected', 'Locked', 'ReadProtected', 'HoldFirst',
    'HoldRest', 'HoldAll', 'HoldAllComplete', 'NHoldFirst', 'NHoldRest',
    'NHoldAll', 'SequenceHold', 'Temporary', 'Stub'])


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
        assert isinstance(path, Expression) and path.head == Symbol('System`List')
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
        # assert all([isinstance(c, str) for c in context_path])
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
        assert ownvalues.head == Symbol('System`List') and len(ownvalues.leaves) == 1
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
        # assert isinstance(name, str)
        attributes = self.get_definition(name).attributes
        # assert attributes.head == Symbol('System`List')
        # assert all(leaf.get_name().startswith('System`') for leaf in attributes.leaves)
        return [leaf.get_name()[7:] for leaf in attributes.leaves]

    def set_attributes(self, name, attributes):
        assert isinstance(name, str)
        assert isinstance(attributes, list)
        # assert all(isinstance(attribute, str) and attribute in known_attributes
        #           for attribute in attributes)
        name = self.lookup_name(name)
        defn = self.get_definition(name)
        defn.attributes = Expression(Symbol('System`List'))
        defn.attributes.leaves = [Symbol('System`' + attribute) for attribute in attributes]

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
