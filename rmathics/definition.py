class Definitions(object):
    """
    Symbol table of definitions (to be filled with Definition instances)
    """
    def __init__(self):
        self.builtin = {}
        self.user = {}

        # TODO load builtins

    def get_current_context(self):
        # TODO
        return "Global`"

    def get_definition(self, name):
        """
        Returns the whole Definition associated with name
            - look in user definitions then builtin
            - return None if definition is not found
        """
        name = self.lookup_name(name)
        builtin = self.builtin.get(name, None)
        if builtin is None:
            return self.user.get(name, None)

    def lookup_name(self, name):
        """
        Determine the full name (with context) for a symbol name.
        """
        current_context = self.get_current_context()
        if "`" in name:
            if name.startswith("`"):
                name = current_context + name.lstrip("`")
            return name


class Definition(object):
    """
    Individual definition entry (to be stored in Definitions)
    """
    def __init__(self, name):
        self.name = name

        self.rules = []
        self.ownvalues = []
        self.downvalues = []
        self.subvalues = []
        self.upvalues = []
        self.formatvalues = []
        self.options = []
        self.nvalues = []
        self.defaultvalues = []
        self.messages = []


def fully_qualified_symbol_name(name):
    return (isinstance(name, basestring)
            and '`' in name
            and not name.startswith('`')
            and not name.endswith('`')
            and '``' not in name)


def ensure_context(name):
    if '`' in name:
        if fully_qualified_symbol_name(name):
            return name
        else:
            raise ValueError("abc")
    return 'System`' + name
