# from __future__ import unicode_literals

import os
import re

from rmathics.expression import (Expression, Symbol, String, ensure_context,
                                 fully_qualified_symbol_name)
from rmathics.characters import letters, letterlikes
from rmathics.rules import Rule
from rmathics.pattern import AtomPattern


names_wildcards = "@*"
base_names_pattern = r'((?![0-9])([0-9${0}{1}{2}])+)'.format(
    letters, letterlikes, names_wildcards)
full_names_pattern = r'(`?{0}(`{0})*)'.format(base_names_pattern)


def get_file_time(file):
    try:
        return os.stat(file).st_mtime
    except OSError:
        return 0


def valuesname(name):
    " 'NValues' -> 'n' "

    assert name.startswith('System`'), name
    if name == 'System`Messages':
        return 'messages'
    else:
        return name[7:-6].lower()


class Definitions(object):
    """
    Symbol table of definitions (to be filled with Definition instances)
    """
    def __init__(self, add_builtin=False, builtin_filename=None):
        self.builtin = {}
        self.user = {}
        self.set_ownvalue('System`$Context', String('Global`'))
        # self.set_ownvalue('System`$ContextPath', Expression(Symbol('List'), String('System`'), String('Global`')))

        # TODO load builtin

    def get_current_context(self):
        # It's crucial to specify System` in this get_ownvalue() call,
        # otherwise we'll end up back in this function and trigger
        # infinite recursion.
        context_rule = self.get_ownvalue('System`$Context')
        context = context_rule.replace.value
        assert context is not None, "$Context somehow set to an invalid value"
        return context

    def get_context_path(self):
        context_path_rule = self.get_ownvalue('System`$ContextPath')
        context_path = context_path_rule.replace
        # assert context_path.has_form('System`List', None)
        context_path = [c.getstr() for c in context_path.leaves]
        # assert not any([c is None for c in context_path])
        return context_path

    def set_current_context(self, context):
        assert isinstance(context, basestring)
        self.set_ownvalue('System`$Context', String(context))

    def set_context_path(self, context_path):
        assert isinstance(context_path, list)
        assert all([isinstance(c, basestring) for c in context_path])
        self.set_ownvalue('System`$ContextPath',
                          Expression('System`List',
                                     *[String(c) for c in context_path]))

    def get_builtin_names(self):
        return set(self.builtin)

    def get_user_names(self):
        return set(self.user)

    def get_names(self):
        return self.get_builtin_names() | self.get_user_names()

    def get_accessible_contexts(self):
        "Return the contexts reachable though $Context or $ContextPath."
        accessible_ctxts = set(self.get_context_path())
        accessible_ctxts.add(self.get_current_context())
        return accessible_ctxts

    def get_matching_names(self, pattern):
        """
        Return a list of the symbol names matching a string pattern.

        A pattern containing a context mark (of the form
        "ctx_pattern`short_pattern") matches symbols whose context and
        short name individually match the two patterns. A pattern
        without a context mark matches symbols accessible through
        $Context and $ContextPath whose short names match the pattern.

        '*' matches any sequence of symbol characters or an empty
        string. '@' matches a non-empty sequence of symbol characters
        which aren't uppercase letters. In the context pattern, both
        '*' and '@' match context marks.
        """

        if re.match(full_names_pattern, pattern) is None:
            # The pattern contained characters which weren't allowed
            # in symbols and aren't valid wildcards. Hence, the
            # pattern can't match any symbols.
            return []

        # If we get here, there aren't any regexp metacharacters in
        # the pattern.

        if '`' in pattern:
            ctx_pattern, short_pattern = pattern.rsplit('`', 1)
            ctx_pattern = ((ctx_pattern + '`')
                           .replace('@', '[^A-Z`]+')
                           .replace('*', '.*')
                           .replace('$', r'\$'))
        else:
            short_pattern = pattern
            # start with a group matching the accessible contexts
            ctx_pattern = ("(?:"
                           + "|".join(re.escape(c) for c in
                                      self.get_accessible_contexts())
                           + ")")

        short_pattern = (short_pattern
                         .replace('@', '[^A-Z]+')
                         .replace('*', '[^`]*')
                         .replace('$', r'\$'))
        regex = re.compile('^' + ctx_pattern + short_pattern + '$')

        return [name for name in self.get_names() if regex.match(name)]

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

        # assert isinstance(name, basestring)

        # Bail out if the name we're being asked to look up is already
        # fully qualified.
        if fully_qualified_symbol_name(name):
            return name

        current_context = self.get_current_context()

        if '`' in name:
            if name.startswith('`'):
                return current_context + name.lstrip('`')
            return name

        with_context = current_context + name
        if not self.have_definition(with_context):
            for ctx in self.get_context_path():
                n = ctx + name
                if self.have_definition(n):
                    return n
        return with_context

    def shorten_name(self, name_with_ctx):
        if '`' not in name_with_ctx:
            return name_with_ctx

        def in_ctx(name, ctx):
            return name.startswith(ctx) and '`' not in name[len(ctx):]

        if in_ctx(name_with_ctx, self.get_current_context()):
            return name_with_ctx[len(self.get_current_context()):]
        for ctx in self.get_context_path():
            if in_ctx(name_with_ctx, ctx):
                return name_with_ctx[len(ctx):]
        return name_with_ctx

    def have_definition(self, name):
        return self.get_definition(name, only_if_exists=True) is not None

    def get_definition(self, name, only_if_exists=False):
        name = self.lookup_name(name)
        user = self.user.get(name, None)
        builtin = self.builtin.get(name, None)

        if user is None and builtin is None:
            return None if only_if_exists else Definition(name=name)
        if builtin is None:
            return user
        if user is None:
            return builtin

        if user:
            attributes = user.attributes
        elif builtin:
            attributes = builtin.attributes
        else:
            attributes = set()
        if not user:
            user = Definition(name=name)
        if not builtin:
            builtin = Definition(name=name)
        options = builtin.options.copy()
        options.update(user.options)
        formatvalues = builtin.formatvalues.copy()
        for form, rules in user.formatvalues.iteritems():
            if form in formatvalues:
                formatvalues[form].extend(rules)
            else:
                formatvalues[form] = rules

        return Definition(name=name,
                          ownvalues=user.ownvalues + builtin.ownvalues,
                          downvalues=user.downvalues + builtin.downvalues,
                          subvalues=user.subvalues + builtin.subvalues,
                          upvalues=user.upvalues + builtin.upvalues,
                          formatvalues=formatvalues,
                          messages=user.messages + builtin.messages,
                          attributes=attributes,
                          options=options,
                          nvalues=user.nvalues + builtin.nvalues,
                          defaultvalues=user.defaultvalues +
                          builtin.defaultvalues,
                          )

    def get_attributes(self, name):
        return self.get_definition(name).attributes

    def get_ownvalues(self, name):
        return self.get_definition(name).ownvalues

    def get_downvalues(self, name):
        return self.get_definition(name).downvalues

    def get_subvalues(self, name):
        return self.get_definition(name).subvalues

    def get_upvalues(self, name):
        return self.get_definition(name).upvalues

    def get_formats(self, name, format=''):
        formats = self.get_definition(name).formatvalues
        result = formats.get(format, []) + formats.get('', [])
        result.sort()
        return result

    def get_nvalues(self, name):
        return self.get_definition(name).nvalues

    def get_defaultvalues(self, name):
        return self.get_definition(name).defaultvalues

    def get_value(self, name, pos, pattern, evaluation):
        assert isinstance(name, basestring)
        assert '`' in name
        rules = self.get_definition(name).get_values_list(valuesname(pos))
        for rule in rules:
            result = rule.apply(pattern, evaluation)
            if result is not None:
                return result

    def get_user_definition(self, name, create=True):
        assert not isinstance(name, Symbol)

        existing = self.user.get(name, None)
        if existing is not None:
            return existing
        else:
            if not create:
                return None
            builtin = self.builtin.get(name, None)
            if builtin is not None:
                attributes = builtin.attributes
            else:
                attributes = []
            self.user[name] = Definition(name=name, attributes=attributes)
            return self.user[name]

    def reset_user_definition(self, name):
        assert not isinstance(name, Symbol)
        del self.user[self.lookup_name(name)]

    def add_user_definition(self, name, definition):
        assert not isinstance(name, Symbol)
        self.user[self.lookup_name(name)] = definition

    def set_attribute(self, name, attribute):
        definition = self.get_user_definition(self.lookup_name(name))
        definition.attributes.add(attribute)

    def set_attributes(self, name, attributes):
        definition = self.get_user_definition(self.lookup_name(name))
        definition.attributes = set(attributes)

    def clear_attribute(self, name, attribute):
        definition = self.get_user_definition(self.lookup_name(name))
        if attribute in definition.attributes:
            definition.attributes.remove(attribute)

    def add_rule(self, name, rule, position=None):
        name = self.lookup_name(name)
        if position is None:
            return self.get_user_definition(name).add_rule(rule)
        else:
            return self.get_user_definition(name).add_rule_at(rule, position)

    def add_format(self, name, rule, form=''):
        definition = self.get_user_definition(self.lookup_name(name))
        if isinstance(form, tuple) or isinstance(form, list):
            forms = form
        else:
            forms = [form]
        for form in forms:
            if form not in definition.formatvalues:
                definition.formatvalues[form] = []
            insert_rule(definition.formatvalues[form], rule)

    def add_nvalue(self, name, rule):
        definition = self.get_user_definition(self.lookup_name(name))
        definition.add_rule_at(rule, 'n')

    def add_default(self, name, rule):
        definition = self.get_user_definition(self.lookup_name(name))
        definition.add_rule_at(rule, 'default')

    def add_message(self, name, rule):
        definition = self.get_user_definition(self.lookup_name(name))
        definition.add_rule_at(rule, 'messages')

    def set_values(self, name, values, rules):
        pos = valuesname(values)
        definition = self.get_user_definition(self.lookup_name(name))
        definition.set_values_list(pos, rules)

    def get_options(self, name):
        return self.get_definition(self.lookup_name(name)).options

    # def reset_user_definitions(self):
    #     self.user = {}

    # def get_user_definitions(self):
    #     return base64.b64encode(
    #         pickle.dumps(self.user, protocol=pickle.HIGHEST_PROTOCOL))

    # def set_user_definitions(self, definitions):
    #     if definitions:
    #         self.user = pickle.loads(base64.b64decode(definitions))
    #     else:
    #         self.user = {}

    def get_ownvalue(self, name):
        ownvalues = self.get_definition(self.lookup_name(name)).ownvalues
        if ownvalues:
            return ownvalues[0]
        return None

    def set_ownvalue(self, name, value):
        from expression import Symbol
        from rules import Rule

        name = self.lookup_name(name)
        self.add_rule(name, Rule(Symbol(name), value))

    def set_options(self, name, options):
        definition = self.get_user_definition(self.lookup_name(name))
        definition.options = options

    def unset(self, name, expr):
        definition = self.get_user_definition(self.lookup_name(name))
        return definition.remove_rule(expr)


def get_tag_position(pattern, name):
    if pattern.get_name() == name:
        return 'ownvalues'
    elif pattern.is_atom():
        return None
    else:
        head_name = pattern.get_head_name()
        if head_name == name:
            return 'downvalues'
        elif head_name == 'System`Condition' and len(pattern.leaves) > 0:
            return get_tag_position(pattern.leaves[0], name)
        elif pattern.get_lookup_name() == name:
            return 'subvalues'
        else:
            for leaf in pattern.leaves:
                if leaf.get_lookup_name() == name:
                    return 'upvalues'
        return None


def insert_rule(values, rule):
    for index, existing in enumerate(values):
        if existing.pattern == rule.pattern:
            del values[index]
            break
    values.insert(0, rule)
    # values.sort() # TODO


class Definition(object):
    """
    Individual definition entry (to be stored in Definitions)
    """
    def __init__(self, name, rules =[], ownvalues=[], downvalues=[], subvalues=[],
                 upvalues=[], formatvalues={}, messages=[], attributes=[],
                 options=[], nvalues=[], defaultvalues={}):
        self.name = name
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

    def get_values_list(self, pos):
        if pos == 'rules':
            return self.rules
        elif pos == 'ownvalues':
            return self.ownvalues
        elif pos == 'subvalues':
            return self.subvalues
        elif pos == 'upvalues':
            return self.upvalues
        # elif pos == 'formatvalues'
        #     return self.formatvalues
        elif pos == 'messages':
            return self.messages
        elif pos == 'attributes':
            return self.attributes
        elif pos == 'options':
            return self.options
        elif pos == 'nvalues':
            return self.nvalues
        # elif pos == 'defaultvalues':
        #     return self.defaultvalues
        else:
            raise ValueError(pos)

    def set_values_list(self, pos, rules):
        if pos == 'rules':
            self.rules = rules
        elif pos == 'ownvalues':
            self.ownvalues = rules
        elif pos == 'subvalues':
            self.subvalues = rules
        elif pos == 'upvalues':
            self.upvalues = rules
        # elif pos == 'formatvalues'
        #     self.formatvalues = rules
        elif pos == 'messages':
            self.messages = rules
        elif pos == 'attributes':
            self.attributes = rules
        elif pos == 'options':
            self.options = rules
        elif pos == 'nvalues':
            self.nvalues = rules
        # elif pos == 'defaultvalues':
        #     self.defaultvalues = rules
        else:
            raise ValueError(pos)

    def add_rule_at(self, rule, position):
        values = self.get_values_list(position)
        insert_rule(values, rule)
        return True

    def add_rule(self, rule):
        pos = get_tag_position(rule.pattern, self.name)
        if pos:
            return self.add_rule_at(rule, pos)
        return False

    def remove_rule(self, lhs):
        position = get_tag_position(lhs, self.name)
        if position:
            values = self.get_values_list(position)
            for index, existing in enumerate(values):
                if existing.pattern.expr == lhs:
                    del values[index]
                    return True
        return False

    def __repr__(self):
        s = (
            '<Definition: name: %s, '
            'downvalues: %s, formats: %s, attributes: %s>') % (
                self.name, self.downvalues, self.formatvalues, self.attributes)
        return s.encode('unicode_escape')
