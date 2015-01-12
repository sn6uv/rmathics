from rply import ParserGenerator, LexerGenerator, DirectoryCache
from rply.token import BaseBox, Token
from math import log10

from rmathics.expression import (
    BaseExpression, Expression, Integer, Symbol, String, Rational)
from rmathics.characters import letters, letterlikes, named_characters
from rmathics.rpython_util import replace
from rmathics.convert import int2Integer, str2Integer, str2Real

try:
    import rpython
    from rpython.annotator import model
except:
    rpython = None

# monkey patching of BaseBox required for RPython
BaseBox._attrs_ = ['head', 'leaves', 'parenthesized']


# Symbols can be any letters
base_symb = r'((?![0-9])([0-9${0}{1}])+)'.format(letters, letterlikes)
full_symb = r'(`?{0}(`{0})*)'.format(base_symb)

# Correctly parsing numbers is a pain
digits = r'([0-9]+((`[0-9]*)?))'
digitsdigits = r'(([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)((`[0-9]*)?))'.format(digits)
base = digits
otherrange = 'r[0-9a-zA-Z]'
basedigits = r'({0}\^\^{1}+)'.format(base, otherrange)
basedigitsdigits = r'({0}\^\^({1}+\.{1}*|{1}*\.{1}+))'.format(base, otherrange)
mantissa = r'({0}|{1})'.format(digits, digitsdigits)
sci = r'{0}\*\^\d+'.format(mantissa)
basesci = r'{0}\^\^{1}'.format(base, sci)
number_patterns = [ # order matters here
    basesci, sci, basedigitsdigits, basedigits, digitsdigits, digits]
number = r'|'.join(number_patterns)

tokens = (
    ('number', number),
    ('string', r'"([^\\"]|\\\\|\\"|\\n|\\r|\\r\\n)*"'),
    ('blanks', r'{0}?_(__?)?{0}?'.format(full_symb)),
    ('blankdefault', r'{0}?_\.'.format(full_symb)),
    ('symbol', full_symb),
    ('slotseq_1', r'\#\#\d+'),
    ('slotseq_2', r'\#\#'),
    ('slotsingle_1', r'\#\d+'),
    ('slotsingle_2', r'\#'),
    ('out_1', r'\%\d+'),
    ('out_2', r'\%+'),
    # ('PutAppend', r'\>\>\>'),
    # ('Put', r'\>\>'),
    # ('Get', r'\<\<'),
    # ('file_filename',
    #   r'''
    #    (?P<quote>\"?)                            (?# Opening quotation mark)
    #        [a-zA-Z0-9\`/\.\\\!\-\:\_\$\*\~\?]+   (?# Literal characters)
    #    (?P=quote)                                (?# Closing quotation mark)
    #    '''),
    ('RawLeftBracket', r'\['),
    ('RawRightBracket', r'\]'),
    ('RawLeftBrace', r'\{'),
    ('RawRightBrace', r'\}'),
    ('RawLeftParenthesis', r'\('),
    ('RawRightParenthesis', r'\)'),
    ('RawComma', r'\,'),
    ('Span', r'\;\;'),
    ('MessageName', r'\:\:'),
    ('PatternTest', r'\?'),
    ('Increment', r'\+\+'),
    ('Decrement', r'\-\-'),
    ('Apply2', r'\@\@\@'),
    ('Apply1', r'\@\@'),
    ('Prefix', r'\@'),
    ('Infix', r'\~'),
    ('MapAll', r'\/\/\@'),
    ('Map', r'\/\@'),
    ('Factorial2', r'\!\!'),
    # ('Transpose', r'\uf3c7'),
    # ('Conjugate', r'\uf3c8'),
    # ('ConjugateTranspose', r'\uf3c9'),
    # ('HermitianConjugate', r'\uf3ce'),
    ('Derivative', r'\'+'),
    ('StringJoin', r'\<\>'),
    # ('Integral', r'\u222b'),
    # ('DifferentialD', r'\uf74c'),
    # (PartialD, r'\u2202'),
    # ('Del', r'\u2207'),
    # ('Square', r'\uf520'),
    # ('SmallCircle', r'\u2218'),
    # ('CircleDot', r'\u2299'),
    ('NonCommutativeMultiply', r'\*\*'),
    # ('Cross', r'\uf4a0'),
    ('RawBackslash', r'\\'),
    # ('Diamond', r'\u22c4'),
    # ('Wedge', r'\u22c0'),
    # ('Vee', r'\u22c1'),
    # ('CircleTimes', r'\u2297'),
    # ('CenterDot', r'\u00b7'),
    # ('Star', r'\u22c6'),
    # (Sum, r' \u2211'),
    # (Product, r'\u220f'),
    ('Times', r'\u00d7'),
    ('Divide', r'\u00f7'),
    # ('PlusMinus', r'\u00b1'),
    # ('MinusPlus', r'\u2213'),
    ('SameQ', r'\=\=\='),
    ('op_Equal', r'\=\='),
    ('op_Unequal', r'\!\='),
    ('op_GreaterEqual', r'\>\='),
    ('op_LessEqual', r'\<\='),
    ('UnsameQ', r'\=\!\='),
    ('Greater', r'\>'),
    ('Less', r'\<'),
    ('op_And', r'\&\&'),
    ('op_Or', r'\|\| '),
    # ('Or', r'\u2228'),
    # ('Nor', r'\u22BD'),
    # ('And', r'\u2227'),
    # ('Nand', r'\u22BC'),
    # ('Xor', r'\u22BB'),
    # ('Xnor', r'\uF4A2'),
    ('Factorial', r'\!'),
    ('RepeatedNull', r'\.\.\.'),
    ('Repeated', r'\.\.'),
    ('Alternatives', r'\|'),
    ('StringExpression', r'\~\~'),
    ('Condition', r'\/\;'),
    ('op_Rule', r'\-\>'),
    ('op_RuleDelayed', r'\:\>'),
    ('ReplaceAll', r'\/\.'),
    ('ReplaceRepeated', r'\/\/\.'),
    ('AddTo', r'\+\='),
    ('SubtractFrom', r'\-\= '),
    ('TimesBy', r'\*\='),
    ('RawStar', r'\*'),
    ('DivideBy', r'\/\= '),
    ('RawAmpersand', r'\&'),
    # ('Colon', r'\u2236'),
    ('Postfix', r'\/\/'),
    ('SetDelayed', r'\:\='),
    ('UpSet', r'\^\='),
    ('UpSetDelayed', r'\^\:\='),
    ('Power', r'\^'),
    ('TagSet', r'\/\:'),
    ('RawColon', r'\:'),
    ('RawSlash', r'\/'),
    ('Unset', r'\=\.'),
    ('Set', r'\='),
    ('Semicolon', r'\;'),
    ('RawDot', r'\.'),
    ('Plus', r'\+'),
    ('Minus', r'\-'),
    # (DiscreteShift, r'\uf4a3'),
    # (DiscreteRatio, r'\uf4a4'),
    # (DifferenceDelta, r'\u2206'),
    # ('VerticalTilde', r'\u2240'),
    # ('Coproduct', r'\u2210'),
    # ('Cap', r'\u2322'),
    # ('Cup', r'\u2323'),
    # ('CirclePlus', r'\u2295'),
    # ('CircleMinus', r'\u2296'),
    # ('Intersection', r'\u22c2'),
    # ('Union', r'\u22c3'),
    # ('Equal', r'\uf431'),
    # ('LongEqual', r'\uf7d9'),
    # ('NotEqual', r'\u2260'),
    # ('LessEqual', r'\u2264'),
    # ('LessSlantEqual', r'\u2a7d'),
    # ('GreaterEqual', r' \u2265 '),
    # ('GreaterSlantEqual', r'\u2a7e'),
    # ('VerticalBar', r'\u2223'),
    # ('NotVerticalBar', r'\u2224'),
    # ('DoubleVerticalBar', r'\u2225'),
    # ('NotDoubleVerticalBar', r'\u2226'),
    # ('Element', r'\u2208'),
    # ('NotElement', r'\u2209'),
    # ('Subset', r'\u2282'),
    # ('Superset', r'\u2283'),
    # ('ForAll', r'\u2200'),
    # ('Exists', r'\u2203'),
    # ('NotExists', r'\u2204'),
    # ('Not', r'\u00AC'),
    # ('Equivalent', r'\u29E6'),
    # ('Implies', r'\uF523'),
    # ('RightTee', r'\u22A2'),
    # ('DoubleRightTee', r'\u22A8'),
    # ('LeftTee', r'\u22A3'),
    # ('DoubleLeftTee', r'\u2AE4'),
    # ('SuchThat', r'\u220D'),
    # ('Rule', r'\uF522'),
    # ('RuleDelayed', r'\uF51F'),
    # ('VerticalSeparator', r'\uF432'),
    # ('Therefore', r'\u2234'),
    # ('Because', r'\u2235'),
    # ('Function', r'\uF4A1'),
)


def string_escape(s):
    s = replace(s, '\\\\', '\\')
    s = replace(s, '\\"', '"')
    s = replace(s, '\\r\\n', '\r\n')
    s = replace(s, '\\r', '\r')
    s = replace(s, '\\n', '\n')
    return s


def prelex(s, messages):
    """
    Converts character codes to characters E.g. \.7A -> z, \:004a -> J
    and longnames to characters e.g. \[Theta].

    Also strips (possibly multiline) comments.
    """
    s = str(s)
    assert isinstance(s, str)
    hexdigits = '0123456789abcdefABCDEF'
    replacements = []
    for i, c in enumerate(s[:-1]):
        if c == '\\':
            if i > 0 and s[i - 1] == '\\':   # backslash is escaped
                continue
            if s[i+1] == ':':           # 4 digit hex code
                if (i+5 >= len(s) and
                    s[i+2] in hexdigits and
                    s[i+3] in hexdigits and
                    s[i+4] in hexdigits and
                    s[i+5] in hexdigits):
                    replacements.append(        # int expects str (not unicode)
                        (i, i+6, chr(int(s[i+2:i+6], 16))))
                else:
                    messages.append(('Syntax', 'snthex'))
            elif s[i+1] == '.':        # 2 digit hex code
                if (i+3 >= len(s) and
                    s[i+2] in hexdigits and
                    s[i+3] in hexdigits):
                    replacements.append(        # int expects str (not unicode)
                        (i, i+4, chr(int(s[i+2:i+4], 16))))
                else:
                    messages.append(('Syntax', 'sntoct2'))
            elif s[i+1] == '[':        # longname
                for j in range(i+2, len(s)):
                    if s[j] == ']':
                        # MMA9 behaviour is \[] -> \\[]
                        longname = s[i+2:j]
                        assert isinstance(longname, str)
                        char = named_characters.get(longname, None)
                        if longname == '':
                            # MMA9 behaviour is \[] -> \\[]
                            replacements.append((i+1, j+1, '\\\\[]'))
                        elif char is not None:
                            replacements.append((i, j+1, char))
                        else:
                            messages.append(('Syntax', 'sntufn'))
                        break

    # Make the replacements
    for start, stop, rep in reversed(replacements):
        s = s[:start] + rep + s[stop:]

    while True:
        comment_start = s.find('(*', 0)
        if comment_start == -1:
            break
        assert comment_start >= 0
        comment_end = s.find('*)', comment_start) + 2
        if comment_end == 1:
            raise WaitInputError
        assert comment_end >= 0
        assert s[comment_start:comment_end].startswith('(*')
        assert s[comment_start:comment_end].endswith('*)')
        s = s[:comment_start] + s[comment_end:]
    return s


class TranslateError(Exception):
    pass


class ScanError(TranslateError):
    pass


class InvalidCharError(TranslateError):
    pass


class ParseError(TranslateError):
    pass


class WaitInputError(TranslateError):
    pass


prefix_operators = (
    # ('Del', ['Del']),
    # ('Square', ['Square']),
    # ('ForAll', ['ForAll']),
    # ('Exists', ['Exists']),
    # ('NotExists', ['NotExists']),
)

infix_operators = (
    ('PatternTest', ['PatternTest']),
    ('Apply', ['Apply1']),
    ('Map', ['Map']),
    ('MapAll', ['MapAll']),
    # ('PlusMinus', ['PlusMinus']),
    # ('MinusPlus', ['MinusPlus']),
    # ('RightTee', ['RightTee']),
    # ('DoubleRightTee', ['DoubleRightTee']),
    ('Power', ['Power']),
    # ('LeftTee', ['LeftTee']),
    # ('DoubleLeftTee', ['DoubleLeftTee']),
    # ('Implies', ['Implies']),
    # ('SuchThat', ['SuchThat']),
    ('Condition', ['Condition']),
    ('Rule', ['op_Rule']), # , 'Rule']),
    ('RuleDelayed', ['op_RuleDelayed']), #, 'RuleDelayed']),
    ('ReplaceAll', ['ReplaceAll']),
    ('ReplaceRepeated', ['ReplaceRepeated']),
    ('AddTo', ['AddTo']),
    ('SubtractFrom', ['SubtractFrom']),
    ('TimesBy', ['TimesBy']),
    ('DivideBy', ['DivideBy']),
    # ('Therefore', ['Therefore']),
    # ('Because', ['Because']),
    ('UpSet', ['UpSet']),
    ('UpSetDelayed', ['UpSetDelayed']),
)

flat_infix_operators = (
    ('StringJoin', ['StringJoin']),
    # ('SmallCircle', ['SmallCircle']),
    # ('CircleDot', ['CircleDot']),
    ('NonCommutativeMultiply', ['NonCommutativeMultiply']),
    # ('Cross', ['Cross']),
    ('Dot', ['RawDot']),
    ('Plus', ['Plus']),
    # ('Intersection', ['Intersection']),
    # ('Union', ['Union']),
    # ('Diamond', ['Diamond']),
    # ('Wedge', ['Wedge']),
    # ('Vee', ['Vee']),
    # ('CircleTimes', ['CircleTimes']),
    # ('CirclePlus', ['CirclePlus']),
    # ('CircleMinus', ['CircleMinus']),
    # ('CenterDot', ['CenterDot']),
    # ('VerticalTilde', ['VerticalTilde']),
    # ('Coproduct', ['Coproduct']),
    # ('Cap', ['Cap']),
    # ('Cup', ['Cup']),
    # ('Star', ['Star']),
    ('Backslash', ['RawBackslash']),
    # ('VerticalBar', ['VerticalBar']),
    # ('NotVerticalBar', ['NotVerticalBar']),
    # ('DoubleVerticalBar', ['DoubleVerticalBar']),
    # ('NotDoubleVerticalBar', ['NotDoubleVerticalBar']),
    ('SameQ', ['SameQ']),
    ('UnsameQ', ['UnsameQ']),
    # ('Element', ['Element']),
    # ('NotElement', ['NotElement']),
    # ('Subset', ['Subset']),
    # ('Superset', ['Superset']),
    ('And', ['op_And']), #, 'op_And']),
    # ('Nand', ['Nand']),
    # ('Xor', ['Xor']),
    # ('Xnor', ['Xnor']),
    ('Or', ['op_Or']), #, 'Or']),
    # ('Nor', ['Nor']),
    # ('Equivalent', ['Equivalent']),
    ('Alternatives', ['Alternatives']),
    ('StringExpression', ['StringExpression']),
    # ('Colon', ['Colon']),
    # ('VerticalSeparator', ['VerticalSeparator']),
)

postfix_operators = (
    ('Increment', ['Increment']),
    ('Decrement', ['Decrement']),
    ('Factorial', ['Factorial']),
    ('Factorial2', ['Factorial2']),
    # ('Conjugate', ['Conjugate']),
    # ('Transpose', ['Transpose']),
    # ('ConjugateTranspose', ['ConjugateTranspose', 'HermitianConjugate']),
    ('Repeated', ['Repeated']),
    ('RepeatedNull', ['RepeatedNull']),
    ('Function', ['RawAmpersand']),
)

inequality_operators = (
    ('Equal', ['op_Equal']), #, 'LongEqual', 'Equal']),
    ('Unequal', ['op_Unequal']), #, 'NotEqual']),
    ('Greater', ['Greater']),
    ('Less', ['Less']),
    ('GreaterEqual', ['op_GreaterEqual']), #, 'GreaterEqual', 'GreaterSlantEqual']),
    ('LessEqual', ['op_LessEqual']), #, 'LessEqual', 'LessSlantEqual']),
)

precedence = (
    ('right', ['FormBox']),
    ('left', ['Semicolon']),                  # flat - custom
    # ('left', ['Put', 'PutAppend']),
    ('right', ['Set', 'SetDelayed', 'Function',
     'UpSet', 'UpSetDelayed', 'TagSet', 'Unset']),
    ('left', ['Because']),
    ('right', ['Therefore']),
    ('left', ['VerticalSeparator']),          # flat
    ('left', ['Postfix']),
    ('right', ['Colon']),                     # flat
    ('left', ['RawAmpersand']),
    ('right', ['AddTo', 'SubtractFrom', 'TimesBy', 'DivideBy']),
    ('left', ['ReplaceAll', 'ReplaceRepeated']),
    ('right', ['Rule', 'op_Rule', 'RuleDelayed', 'op_RuleDelayed']),
    ('left', ['Condition']),
    ('left', ['StringExpression']),           # flat
    ('right', ['RawColon']),
    ('left', ['Alternatives']),               # flat
    ('nonassoc', ['Repeated', 'RepeatedNull']),
    ('right', ['SuchThat']),
    ('left', ['LeftTee', 'DoubleLeftTee']),
    ('right', ['RightTee', 'DoubleRightTee']),
    ('right', ['Implies']),
    ('left', ['Equivalent']),                 # flat
    ('left', ['Or', 'op_Or', 'Nor']),         # flat
    ('left', ['Xor', 'Xnor']),                # flat
    ('left', ['And', 'op_And', 'Nand']),      # flat
    # ('right', ['Not']),
    ('right', ['ForAll', 'Exists', 'NotExists']),
    ('left', ['Element', 'NotElement', 'Subset', 'Superset']),    # flat
    ('left', ['SameQ', 'UnsameQ']),           # flat
    ('left', ['Equal', 'op_Equal', 'LongEqual', 'op_Unequal', 'NotEqual',
              'Greater', 'Less', 'GreaterEqual', 'op_GreaterEqual',
              'GreaterSlantEqual', 'LessEqual', 'op_LessEqual',
              'LessSlantEqual', 'VerticalBar', 'NotVerticalBar',
              'DoubleVerticalBar', 'NotDoubleVerticalBar']),
    ('nonassoc', ['Span']),
    ('left', ['Union']),                      # flat
    ('left', ['Intersection']),               # flat
    ('left', ['Plus', 'Minus', 'PlusMinus', 'MinusPlus']),  # flat
    # ('left', ['Sum']),                      # flat
    ('left', ['CirclePlus', 'CircleMinus']),  # flat
    ('left', ['Cap', 'Cup']),                 # flat
    ('left', ['Coproduct']),                  # flat
    ('left', ['VerticalTilde']),              # flat
    # ('left', ['Product']),
    ('left', ['Star']),                       # flat
    # This is a hack to get implicit times working properly:
    ('left', ['Times', 'RawStar', 'blanks', 'blankdefault', 'out',
              'slotsingle1', 'slotsingle2', 'slotseq1', 'slotseq2',
              'string', 'symbol', 'number', 'RawLeftBrace',
              'RawLeftParenthesis']),         # flat,
    ('left', ['CenterDot']),                  # flat
    ('left', ['CircleTimes']),                # flat
    ('left', ['Vee']),                        # flat
    ('left', ['Wedge']),                      # flat
    ('left', ['Diamond']),                    # flat
    ('nonassoc', ['RawBackslash']),
    ('left', ['RawSlash', 'Divide', 'Fraction']),
    ('right', ['UPlus', 'UMinus', 'UPlusMinus', 'UMinusPlus']),
    ('left', ['RawDot']),                     # flat
    ('left', ['Cross']),                      # flat
    ('left', ['NonCommutativeMultiply']),     # flat
    ('right', ['CircleDot']),
    ('left', ['SmallCircle']),                # flat
    ('right', ['Square']),
    ('right', ['Del']),
    ('right', ['Integral', 'DifferentialD']),
    ('right', ['Sqrt']),
    ('right', ['Power', 'Superscript']),
    ('left', ['StringJoin']),                 # flat
    ('left', ['Derivative']),
    ('left', ['Conjugate', 'Transpose', 'ConjugateTranspose']),
    ('left', ['Factorial', 'Factorial2']),
    ('right', ['Apply1', 'Apply2', 'Map', 'MapAll']),
    ('left', ['Infix']),
    ('right', ['Prefix']),
    ('right', ['PreIncrement', 'PreDecrement']),
    ('left', ['Increment', 'Decrement']),
    ('left', ['PART', 'RawLeftBracket', 'RawRightBracket']),
    ('nonassoc', ['PatternTest']),
    ('nonassoc', ['InterpretedBox']),
    ('right', ['Subscript']),
    ('right', ['Overscript', 'Underscript']),
    # ('nonassoc', ['Get']),
    # ('nonassoc', ['blanks', 'blankdefault']),
    # ('nonassoc', ['out']),
    # ('nonassoc', ['slotsingle', 'slotseq']),
    ('nonassoc', ['MessageName']),
    # ('nonassoc', ['string']),
    # ('nonassoc', ['symbol']),
    # ('nonassoc', ['number']),
)

pg = ParserGenerator(
    [token[0] for token in tokens] + ['Function'],
    precedence=precedence,
    cache=DirectoryCache(cache_id="mathics", cache_dir="/home/angus/prog/rmathics/rmathics/cache/parser/")
)

@pg.production('main : expr')
@pg.production('main : ')
def main(state, p):
    if len(p) == 0:
        return None
    elif len(p) == 1:
        return p[0]

@pg.production('expr : number')
def number(state, p):
    value = p[0].getstr()
    if '^^' in value:
        pass
    elif '.' in value:
        # TODO precision
        return str2Real(value, 53)
    else:
        return str2Integer(value)

@pg.production('expr : string')
def string(state, p):
    s = p[0].getstr()
    start, stop = 1, len(s) - 1
    assert stop >= 0
    s = s[start:stop]
    return String(string_escape(s))

@pg.production('expr : slotseq_1')
@pg.production('expr : slotseq_2')
def slotseq(state, p):
    s = p[0].getstr()
    value = 1 if len(s) == 2 else int(s[2:])
    return Expression(Symbol('System`SlotSequence'), int2Integer(value))

@pg.production('expr : slotsingle_1')
@pg.production('expr : slotsingle_2')
def slotsingle(state, p):
    s = p[0].getstr()
    value = 1 if len(s) == 1 else int(s[1:])
    return Expression(Symbol('System`Slot'), int2Integer(value))

@pg.production('expr : out_1')
def out_1(state, p):
    s = p[0].getstr()
    value = int(p[0].getstr()[1:])
    if value == -1:
        return Expression(Symbol('System`Out'))
    else:
        return Expression(Symbol('System`Out'), int2Integer(value))

@pg.production('expr : out_2')
def out_2(state, p):
    s = p[0].getstr()
    value = -len(s)
    if value == -1:
        return Expression(Symbol('System`Out'))
    else:
        return Expression(Symbol('System`Out'), int2Integer(value))

# def t_PutAppend(self, t):
#     r' \>\>\> '
#     t.lexer.begin('file')
#     return t
#
# def t_Put(self, t):
#     r' \>\> '
#     t.lexer.begin('file')
#     return t
#
# def t_Get(self, t):
#     r' \<\< '
#     t.lexer.begin('file')
#     return t
#
# def t_file_filename(self, t):
#     r'''
#     (?P<quote>\"?)                              (?# Opening quotation mark)
#         [a-zA-Z0-9\`/\.\\\!\-\:\_\$\*\~\?]+     (?# Literal characters)
#     (?P=quote)                                  (?# Closing quotation mark)
#     '''
#     s = t.value
#     if s.startswith('"'):
#         s = s[1:-1]
#     s = self.string_escape(s)
#     s = s.replace('\\', '\\\\')
#     t.value = String(s)
#     t.lexer.begin('INITIAL')
#     return t

for prefix_op, prefix_tokens in prefix_operators:
    code = """def %s_prefix(state, p):
    return Expression(Symbol('System`%s'), p[1])""" % (prefix_op, prefix_op)
    for token in prefix_tokens:
        code = ("@pg.production('expr : %s expr')\n" % token) + code
    exec(code)

for infix_op, infix_tokens in infix_operators:
    code = """def %s_infix(state, p):
    return Expression(Symbol('System`%s'), p[0], p[2])""" % (
        infix_op, infix_op)
    for token in infix_tokens:
        code = ("@pg.production('expr : expr %s expr')\n" % token) + code
    exec(code)

for flat_infix_op, flat_infix_tokens in flat_infix_operators:
    code = """def %s_flat_infix(state, p):
    args = []
    if p[0].head.same(Symbol('System`%s')):
        args.extend(p[0].leaves)
    else:
        args.append(p[0])
    if p[2].head.same(Symbol('System`%s')):
        args.extend(p[2].leaves)
    else:
        args.append(p[2])
    expr = Expression(Symbol('System`%s'))
    expr.leaves = args
    return expr""" % (
        flat_infix_op, flat_infix_op, flat_infix_op, flat_infix_op)
    for token in flat_infix_tokens:
        code = ("@pg.production('expr : expr %s expr')\n" % token) + code
    exec(code)

for postfix_op, postfix_tokens in postfix_operators:
    code = """def %s_postfix(state, p):
    return Expression(Symbol('System`%s'), p[0])""" % (postfix_op, postfix_op)
    for token in postfix_tokens:
        code = ("@pg.production('expr : expr %s')\n" % token) + code
    exec(code)

for ineq_op, ineq_tokens in inequality_operators:
    code = """def %s_inequality(state, p):
        head = p[0].head
        ineq_op = 'System`%s'
        if head.same(Symbol(ineq_op)):
            p[0].leaves.append(p[2])
            return p[0]
        elif head.same(Symbol('System`Inequality')):
            p[0].leaves.append(Symbol(ineq_op))
            p[0].leaves.append(p[2])
            return p[0]
        elif head.get_name() in ['System`%%s' %% k[0] for k in list(inequality_operators)]:
            leaves = []
            for i, leaf in enumerate(p[0].leaves):
                if i != 0:
                    leaves.append(head)
                leaves.append(leaf)
            leaves.append(Symbol(ineq_op))
            leaves.append(p[0])
            expr = Expression(Symbol('System`Inequality'))
            expr.leaves = leaves
            return expr
        else:
            return Expression(Symbol(ineq_op), p[0], p[2])""" % (
        ineq_op, ineq_op)
    for token in ineq_tokens:
        code = ("@pg.production('expr : expr %s expr')\n" % token) + code
    exec(code)

@pg.error
def error_handler(state, token):
    sourcepos = token.getsourcepos()
    if sourcepos is not None:
        if sourcepos.idx == 0:
            # TODO raise: Syntax:sntxb
            state.messages.append(('Syntax', 'sntxb'))
            pass
        else:
            # TODO raise: Syntax:sntxf
            state.messages.append(('Syntax', 'sntxf'))
            pass
    if token.gettokentype() == '$end':
        raise WaitInputError()
    raise ParseError(token.gettokentype())

@pg.production('expr : RawLeftParenthesis expr RawRightParenthesis')
def parenthesis(state, p):
    expr = p[1]
    expr.parenthesized = True
    return expr

class SequenceBox(BaseBox):
    def __init__(self, leaves):
        self.leaves = leaves

@pg.production('expr : expr args', precedence='PART')
def call(state, p):
    expr = Expression(p[0])
    expr.leaves = p[1].leaves
    expr.parenthesized = True  # to handle e.g. Power[a,b]^c correctly
    return expr

@pg.production('expr : expr position', precedence='PART')
def part(state, p):
    expr = Expression(Symbol('System`Part'))
    expr.leaves = [p[0]] + p[1].leaves
    expr.parenthesized = True  # to handle e.g. Power[a,b]^c correctly
    return expr

@pg.production('args : RawLeftBracket sequence RawRightBracket')
def args(state, p):
    return p[1]

@pg.production('expr : RawLeftBrace sequence RawRightBrace')
def llist(state, p): # name prevents collision with builtin list
    expr = Expression(Symbol('System`List'))
    expr.leaves = p[1].leaves
    return expr

@pg.production('position : RawLeftBracket RawLeftBracket sequence RawRightBracket RawRightBracket')
def position(state, p):
    return p[2]

@pg.production('sequence :')
@pg.production('sequence : expr')
@pg.production('sequence : sequence RawComma sequence')
def sequence(state, p):
    assert len(p) in (0, 1, 3)
    if len(p) == 0:
        return SequenceBox([])
    elif len(p) == 1:
        return SequenceBox([p[0]])
    elif len(p) == 3:
        if p[0].leaves == []:
            state.messages.append(('Syntax', 'com'))
            p[0].leaves = [Symbol('System`Null')]
        if p[2].leaves == []:
            state.messages.append(('Syntax', 'com'))
            p[2].leaves = [Symbol('System`Null')]
        return SequenceBox(p[0].leaves + p[2].leaves)
    else:
        raise ValueError

@pg.production('expr : symbol')
def symbol(state, p):
    name = p[0].getstr()
    return Symbol(state.definitions.lookup_name(name))

@pg.production('pattern : blanks')
def blanks(state, p):
    pieces = p[0].getstr().split('_')
    count = len(pieces) - 1
    assert 1 <= count <= 3
    if count == 1:
        name = 'System`Blank'
    elif count == 2:
        name = 'System`BlankSequence'
    elif count == 3:
        name = 'System`BlankNullSequence'
    else:
        raise ValueError    # required for RPython annotator
    if pieces[-1]:
        piece = Token('symbol', pieces[-1])
        # p[0].getsourcepos() + len(''.join(pieces[:-1]))
        blank = Expression(Symbol(name), symbol(state, [piece]))
    else:
        blank = Expression(Symbol(name))
    if pieces[0]:
        piece = Token('symbol', pieces[0])
        # p[0].getsourcepos() + len(''.join(pieces[1:]))
        return Expression(Symbol('System`Pattern'), symbol(state, [piece]), blank)
    else:
        return blank

@pg.production('pattern : blankdefault')
def blankdefault(state, p):
    assert isinstance(p[0], str) and len(p[0]) >= 2
    name = p[0][:-2]
    if name:
        return Expression(Symbol('System`Optional'), Expression(
            Symbol('System`Pattern'), Symbol(state.definitions.lookup_name(name)), Expression(Symbol('System`Blank'))))
    else:
        return Expression(Symbol('System`Optional'), Expression(Symbol('System`Blank')))

@pg.production('expr : pattern')
def pattern(state, p):
    return p[0]

# def p_Get(self, args):
#     'expr : Get filename'
#     args[0] = Expression(Symbol('System`Get'), args[2])

@pg.production('expr : expr MessageName symbol MessageName symbol')
@pg.production('expr : expr MessageName string MessageName symbol')
@pg.production('expr : expr MessageName symbol MessageName string')
@pg.production('expr : expr MessageName string MessageName string')
@pg.production('expr : expr MessageName symbol')
@pg.production('expr : expr MessageName string')
def MessageName(state, p):
    assert len(p) in (3, 5)
    if p[2].getstr().startswith('"'):
        p2 = string(state, [p[2]])
    else:
        p2 = symbol(state, [p[2]])
    if len(p) == 3:
        return Expression(Symbol('System`MessageName'), p[0], p2)
    elif len(p) == 5:
        if p[4].getstr().startswith('"'):
            p4 = string(state, [p[4]])
        else:
            p4 = symbol(state, [p[4]])
        return Expression(Symbol('System`MessageName'), p[0], p2, p4)

@pg.production('expr : Increment expr', precedence='PreIncrement')
def PreIncrement(state, p):
    return Expression(Symbol('System`PreIncrement'), p[1])

@pg.production('expr : Decrement expr', precedence='PreDecrement')
def PreDecrement(state, p):
    return Expression(Symbol('System`PreDecrement'), p[1])

@pg.production('expr : expr Prefix expr')
def Prefix(state, p):
    return Expression(p[0], p[2])

@pg.production('expr : expr Infix expr Infix expr')
def p_Infix(state, p):
    return Expression(p[2], p[0], p[4])

@pg.production('expr : expr Apply2 expr')
def p_Apply2(state, p):
    return Expression(
        Symbol('System`Apply'), p[0], p[2],
        Expression(Symbol('System`List'), int2Integer(1)))

@pg.production('expr : expr Derivative')
def Derivative(state, p):
    n = len(p[1].getstr())
    is_derivative = (isinstance(p[0], Expression) and
                     p[0].head.same(Symbol('System`Derivative')) and
                     isinstance(p[0].head.leaves[0], Integer))
    if isinstance(p[0].head, Expression) and p[0].head.head.same(Symbol('System`Derivative')):
        head = p[0].head
        leaves = p[0].leaves
        if len(head.leaves) == 1 and isinstance(head.leaves[0], Integer) and len(leaves) == 1:
            n += head.leaves[0].to_int()
            p[0] = leaves[0]
    return Expression(
        Expression(Symbol('System`Derivative'), int2Integer(n)), p[0])

# @pg.production('expr : Integral expr DifferentialD expr',
#                precedence='Integral')
# def Integrate(state, p):
#     return Expression(Symbol('System`Integrate'), p[1], p[3])

@pg.production('expr : expr Minus expr')
def Minus(state, p):
    return Expression(Symbol('System`Plus'), p[0],
                      Expression(Symbol('System`Times'), int2Integer(-1), p[2]))

@pg.production('expr : Plus expr', precedence='UPlus')
def UPlus(state, p):
    return p[1]

@pg.production('expr : Minus expr', precedence='UMinus')
def UMinus(state, p):
    # if isinstance(p[0], (Integer, Real)):
    # TODO
    return Expression(Symbol('System`Times'), int2Integer(-1), p[1])

# @pg.production('expr : PlusMinus expr', precedence='UPlusMinus')
# def UPlusMinus(state, p):
#     return Expression(Symbol('System`PlusMinus'), p[1])
# 
# @pg.production('expr : MinusPlus expr', precedence='UMinusPlus')
# def UMinusPlus(state, p):
#     return Expression(Symbol('System`MinusPlus'), p[1])

@pg.production('expr : expr RawSlash expr')
@pg.production('expr : expr Divide expr')
def Divide(state, p):
    return Expression(Symbol('System`Times'), p[0],
                      Expression(Symbol('System`Power'), p[2], int2Integer(-1)))

@pg.production('expr : expr Times expr')
@pg.production('expr : expr RawStar expr')
@pg.production('expr : expr expr', precedence='Times')
def Times(state, p):
    assert 2 <= len(p) <= 3
    if len(p) == 2:
        arg1, arg2 = p[0], p[1]
    elif len(p) == 3:
        arg1, arg2 = p[0], p[2]
    else:
        raise ValueError    # required for RPython annotator

    # flatten
    args = []
    if arg1.head.same(Symbol('System`Times')):
        args.extend(arg1.leaves)
    else:
        args.append(arg1)
    if arg2.head.same(Symbol('System`Times')):
        args.extend(arg2.leaves)
    else:
        args.append(arg2)
    expr = Expression(Symbol('System`Times'))
    expr.leaves = args
    return expr

@pg.production('expr :      Span')
@pg.production('expr :      Span expr')
@pg.production('expr : expr Span')
@pg.production('expr : expr Span expr')
@pg.production('expr :      Span      Span expr')
@pg.production('expr :      Span expr Span expr')
@pg.production('expr : expr Span      Span expr')
@pg.production('expr : expr Span expr Span expr')
def Span(state, p):
    if len(p) == 5:
        return Expression(Symbol('System`Span'), p[0], p[2], p[4])
    elif len(p) == 4:
        if isinstance(p[0], BaseExpression):
            return Expression(Symbol('System`Span'), p[0], Symbol('All'), p[3])
        elif isinstance(p[1], BaseExpression):
            return Expression(Symbol('System`Span'), int2Integer(1), p[1], p[3])
    elif len(p) == 3:
        if isinstance(p[0], BaseExpression):
            return Expression(Symbol('System`Span'), p[0], p[2])
        else:
            return Expression(Symbol('System`Span'), int2Integer(1),
                              Symbol('System`All'), p[2])
    elif len(p) == 2:
        if isinstance(p[0], BaseExpression):
            return Expression(Symbol('System`Span'), p[0], Symbol('All'))
        elif isinstance(p[1], BaseExpression):
            return Expression(Symbol('System`Span'), int2Integer(1), p[1])
    elif len(p) == 1:
            return Expression(Symbol('System`Span'), int2Integer(1), Symbol('All'))

# @pg.production('expr : Not expr')
# FIXME
# @pg.production('expr : Factorial2 expr', precedence='Not')
# @pg.production('expr : Factorial expr', precedence='Not')
# def Not(state, p):
#     if p[0].getstr() == '!!':
#         return Expression(
#             Symbol('System`Not'), Expression(Symbol('System`Not'), p[1]))
#     else:
#         return Expression(Symbol('System`Not'), p[1])

@pg.production('expr : symbol RawColon pattern RawColon expr')
@pg.production('expr : symbol RawColon expr')
def Pattern(state, p):
    p0 =  symbol(state, [p[0]])
    if len(p) == 5:
        return Expression(
            Symbol('System`Optional'), Expression(Symbol('System`Pattern'), p0, p[2]), p[4])
    elif len(p) == 3:
        if p[2].head.same(Symbol('System`Pattern')):
            return Expression(
                Symbol('System`Optional'),
                Expression(Symbol('System`Pattern'), p0, p[2].leaves[0]),
                p[2].leaves[1])
        else:
            return Expression(Symbol('System`Pattern'), p0, p[2])

@pg.production('expr : pattern RawColon expr')
def Optional(state, p):
    return Expression(Symbol('System`Optional'), p[0], p[2])

@pg.production('expr : expr Postfix expr')
def Postfix(state, p):
    return Expression(p[2], p[0])

@pg.production('expr : expr TagSet expr Set expr')
@pg.production('expr : expr Set expr')
def Set(state, p):
    if len(p) == 3:
        return Expression(Symbol('System`Set'), p[0], p[2])
    elif len(p) == 5:
        return Expression(Symbol('System`TagSet'), p[0], p[2], p[4])

@pg.production('expr : expr TagSet expr SetDelayed expr')
@pg.production('expr : expr SetDelayed expr')
def SetDelayed(state, p):
    if len(p) == 3:
        return Expression(Symbol('System`SetDelayed'), p[0], p[2])
    elif len(p) == 5:
        return Expression(Symbol('System`TagSetDelayed'), p[0], p[2], p[4])

@pg.production('expr : expr TagSet expr Unset')
@pg.production('expr : expr Unset')
def p_Unset(state, p):
    if len(p) == 2:
        return Expression(Symbol('System`Unset'), p[0])
    elif len(p) == 4:
        return Expression(Symbol('System`TagUnset'), p[0], p[2])

@pg.production('expr : expr Function expr')
def Function(state, p):
    return Expression(Symbol('System`Function'),
                      Expression(Symbol('System`List'), p[0]),
                      p[2])

# def p_Put(self, args):
#     'expr : expr Put filename'
#     args[0] = Expression(Symbol('System`Put'), args[1], args[3])
#
# def p_PutAppend(self, args):
#     'expr : expr PutAppend filename'
#     args[0] = Expression(Symbol('System`PutAppend'), args[1], args[3])

@pg.production('expr : expr Semicolon expr')
@pg.production('expr : expr Semicolon')
def Compound(state, p):
    if p[0].head.same(Symbol('System`CompoundExpression')):
        # TODO?
        pass
    else:
        p[0] = Expression(Symbol('System`CompoundExpression'), p[0])
    if len(p) == 3:
        p[0].leaves.append(p[2])
    else:
        p[0].leaves.append(Symbol('System`Null'))
    return p[0]


class ParserState(object):
    """
    Object for storing parser state:
      - definitions used (e.g. looking up symbol names)
      - messages created (e.g. invalid \[xxxx] longnames)
    """
    def __init__(self, messages, definitions):
        self.messages = messages
        self.definitions = definitions

# Construct lexer
lg = LexerGenerator()
for token, regex in tokens:
    lg.add(token, regex)
lg.ignore(r'\s+')
lexer = lg.build()

# Construct parser
parser = pg.build()


def parse(string, definitions):
    """
    Parses a string and returns an expression (or None if the string is empty)
    also return the messages generated during parsing
    """
    state = ParserState([], definitions)
    result = parser.parse(lexer.lex(prelex(string, state.messages)), state=state)
    return (result, state.messages)
