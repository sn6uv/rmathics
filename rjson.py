'''
Parses a tiny subset of JSON

Assumes:
    - no unecessary whitespace (except within strings)
    - every field is a string
    - every value is either string, int, bool, dict or list.
'''


class Node(object):
    def __init__(self):
        pass


class JStr(Node):
    def __init__(self, value):
        self._str = value

    def dumps(self):
        return '"' + self._str + '"'


class JInt(Node):
    def __init__(self, value):
        self._int = value

    def dumps(self):
        return str(self._int)


class JBool(Node):
    def __init__(self, value):
        self._bool = value

    def dumps(self):
        return 'true' if self._bool else 'false'


class JDict(Node):
    def __init__(self, value):
        self._dict = value

    def dumps(self):
        return '{' + ', '.join(['"' + key + '":' + (self._dict[key]).dumps() for key in self._dict]) + '}'

    def __getitem__(self, key):
        return self._dict[key]


class JList(Node):
    def __init__(self, value):
        self._list = value

    def dumps(self):
        return '[' + ', '.join([value.dumps() for value in self._list]) + ']'


def _lrstrip1(s):
    '''
    returns s[1:-1]
    '''
    istart = 1
    istop = len(s) - 1
    assert istop >= 1
    return s[istart:istop]


def loads(s):
    d = {}
    assert s[0] == '{' and s[-1] == '}'
    s = _lrstrip1(s)
    if s == '':
        return JDict({})
    for entry in s.split(','):
        field, value = entry.split(':', 1)
        field = field
        value = value
        assert field[0] == field[-1] == '"'
        field = _lrstrip1(field)
        if value[0] == value[-1] == '"':
            value = JStr(_lrstrip1(value))
        elif value.isdigit():
            value = JInt(int(value))
        elif value in ('true', 'false'):
            value = JBool(value == 'true')
        elif value[0] == '[' and value[-1] == ']':
            value = JList([loads(v) for v in _lrstrip1(value).split(',')])
        elif value[0] == '{' and value[-1] == '}':
            value = loads(value)
        else:
            print(value)
            raise ValueError("cannot parse %s" % value)
        d[field] = value
    return JDict(d)
