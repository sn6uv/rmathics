from rply import ParserGenerator, LexerGenerator
from math import log10

from rmathics.expression import (
    BaseExpression, Expression, Integer, Real, Symbol, String, Rational,
    ensure_context)
from rmathics.characters import letters, letterlikes, named_characters
from rmathics.convert import str_to_num


# Symbols can be any letters
base_symb = ur'((?![0-9])([0-9${0}{1}])+)'.format(letters, letterlikes)
full_symb = ur'(`?{0}(`{0})*)'.format(base_symb)

tokens = (
    ('number', r'((\d+\^\^([a-zA-Z0-9]+\.?[a-zA-Z0-9]*|[a-zA-Z0-9]*\.?[a-zA-Z0-9]+))|(\d+\.?\d*|\d*\.?\d+))(``?(\+|-)?(\d+\.?\d*|\d*\.?\d+)|`)?(\*\^(\+|-)?\d+)?'),
    ('string', r'"([^\\"]|\\\\|\\"|\\n|\\r|\\r\\n)*"'),
    ('blankdefault', ur'{0}?_\.'.format(full_symb)),
    ('blanks', ur'{0}?_(__?)?{0}?'.format(full_symb)),
    ('symbol', full_symb),
    ('slotseq_1', r'\#\#\d+'),
    ('slotseq_2', r'\#\#'),
    ('slotsingle_1', r'\#\d+'),
    ('slotsingle_2', r'\#'),
    ('out_1', r'\%\d+'),
    ('out_2', r'\%+'),
    ('PutAppend', r'\>\>\>'),
    ('Put', r'\>\>'),
    ('Get', r'\<\<'),
    # ('file_filename',
    #    r'''
    #    (?P<quote>\"?)                              (?# Opening quotation mark)
    #        [a-zA-Z0-9\`/\.\\\!\-\:\_\$\*\~\?]+     (?# Literal characters)
    #    (?P=quote)                                  (?# Closing quotation mark)
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
    ('Prefix', r'\@'),
    ('Infix', r'\~'),
    ('Apply1', r'\@\@'),
    ('Apply2', r'\@\@\@'),
    ('Map', r'\/\@'),
    ('MapAll', r'\/\/\@'),
    ('Factorial', r'\!'),
    ('Factorial2', r'\!\!'),
    ('Transpose', ur'\uf3c7'),
    ('Conjugate', ur'\uf3c8'),
    ('ConjugateTranspose', ur'\uf3c9'),
    ('HermitianConjugate', ur'\uf3ce'),
    ('Derivative', r'\'+'),
    ('StringJoin', r'\<\>'),
    ('Power', r'\^'),
    ('Integral', ur'\u222b'),
    ('DifferentialD', ur'\uf74c'),
    # (PartialD, ur'\u2202'),
    ('Del', ur'\u2207'),
    ('Square', ur'\uf520'),
    ('SmallCircle', ur'\u2218'),
    ('CircleDot', ur'\u2299'),
    ('NonCommutativeMultiply', r'\*\*'),
    ('Cross', ur'\uf4a0'),
    ('RawDot', r'\.'),
    ('Plus', r'\+'),
    ('Minus', r'\-'),
    ('RawSlash', r'\/'),
    ('RawBackslash', r'\\'),
    ('Diamond', ur'\u22c4'),
    ('Wedge', ur'\u22c0'),
    ('Vee', ur'\u22c1'),
    ('CircleTimes', ur'\u2297'),
    ('CenterDot', ur'\u00b7'),
    ('Star', ur'\u22c6'),
    # (Sum, ur' \u2211'),
    # (Product, ur'\u220f'),
    ('RawStar', r'\*'),
    ('Times', ur'\u00d7'),
    ('Divide', ur'\u00f7'),
    ('PlusMinus', ur'\u00b1'),
    ('MinusPlus', ur'\u2213'),
    ('op_Equal', r'\=\='),
    ('op_Unequal', r'\!\='),
    ('Greater', r'\>'),
    ('Less', r'\<'),
    ('op_GreaterEqual', r'\>\='),
    ('op_LessEqual', r'\<\='),
    ('SameQ', r'\=\=\='),
    ('UnsameQ', r'\=\!\='),
    ('op_And', r'\&\&'),
    ('op_Or', r'\|\| '),
    ('Or', ur'\u2228'),
    ('Nor', ur'\u22BD'),
    ('And', ur'\u2227'),
    ('Nand', ur'\u22BC'),
    ('Xor', ur'\u22BB'),
    ('Xnor', ur'\uF4A2'),
    ('Repeated', r'\.\.'),
    ('RepeatedNull', r'\.\.\.'),
    ('Alternatives', r'\|'),
    ('RawColon', r'\:'),
    ('StringExpression', r'\~\~'),
    ('Condition', r'\/\;'),
    ('op_Rule', r'\-\>'),
    ('op_RuleDelayed', r'\:\>'),
    ('ReplaceAll', r'\/\.'),
    ('ReplaceRepeated', r'\/\/\.'),
    ('AddTo', r'\+\='),
    ('SubtractFrom', r'\-\= '),
    ('TimesBy', r'\*\='),
    ('DivideBy', r'\/\= '),
    ('RawAmpersand', r'\&'),
    ('Colon', ur'\u2236'),
    ('Postfix', r'\/\/'),
    ('Set', r'\='),
    ('SetDelayed', r'\:\='),
    ('UpSet', r'\^\='),
    ('UpSetDelayed', r'\^\:\='),
    ('TagSet', r'\/\:'),
    ('Unset', r'\=\.'),
    ('Semicolon', r'\;'),
    # (DiscreteShift, ur'\uf4a3'),
    # (DiscreteRatio, ur'\uf4a4'),
    # (DifferenceDelta, ur'\u2206'),
    ('VerticalTilde', ur'\u2240'),
    ('Coproduct', ur'\u2210'),
    ('Cap', ur'\u2322'),
    ('Cup', ur'\u2323'),
    ('CirclePlus', ur'\u2295'),
    ('CircleMinus', ur'\u2296'),
    ('Intersection', ur'\u22c2'),
    ('Union', ur'\u22c3'),
    ('Equal', ur'\uf431'),
    ('LongEqual', ur'\uf7d9'),
    ('NotEqual', ur'\u2260'),
    ('LessEqual', ur'\u2264'),
    ('LessSlantEqual', ur'\u2a7d'),
    ('GreaterEqual', ur' \u2265 '),
    ('GreaterSlantEqual', ur'\u2a7e'),
    ('VerticalBar', ur'\u2223'),
    ('NotVerticalBar', ur'\u2224'),
    ('DoubleVerticalBar', ur'\u2225'),
    ('NotDoubleVerticalBar', ur'\u2226'),
    ('Element', ur'\u2208'),
    ('NotElement', ur'\u2209'),
    ('Subset', ur'\u2282'),
    ('Superset', ur'\u2283'),
    ('ForAll', ur'\u2200'),
    ('Exists', ur'\u2203'),
    ('NotExists', ur'\u2204'),
    ('Not', ur'\u00AC'),
    ('Equivalent', ur'\u29E6'),
    ('Implies', ur'\uF523'),
    ('RightTee', ur'\u22A2'),
    ('DoubleRightTee', ur'\u22A8'),
    ('LeftTee', ur'\u22A3'),
    ('DoubleLeftTee', ur'\u2AE4'),
    ('SuchThat', ur'\u220D'),
    ('Rule', ur'\uF522'),
    ('RuleDelayed', ur'\uF51F'),
    ('VerticalSeparator', ur'\uF432'),
    ('Therefore', ur'\u2234'),
    ('Because', ur'\u2235'),
    ('Function', ur'\uF4A1'),
)

def string_escape(s):
    s = s.replace('\\\\', '\\').replace('\\"', '"')
    s = s.replace('\\r\\n', '\r\n')
    s = s.replace('\\r', '\r')
    s = s.replace('\\n', '\n')
    return s

def prelex(s):
    """
    Converts character codes to characters E.g. \.7A -> z, \:004a -> J
    and longnames to characters e.g. \[Theta]
    """

    hexdigits = u'0123456789abcdefABCDEF'
    replacements = []
    for i, c in enumerate(s[:-1]):
        if c == u'\\':
            if i > 0 and s[i-1] == u'\\':   # backslash is escaped
                continue
            if s[i+1] == u':':           # 4 digit hex code
                if (i + 5 >= len(s) and
                    s[i+2] in hexdigits and
                    s[i+3] in hexdigits and
                    s[i+4] in hexdigits and
                    s[i+5] in hexdigits):
                    replacements.append(        # int expects str (not unicode)
                        (i, i+6, unichr(int(str(s[i+2:i+6]), 16))))
                else:
                    # TODO Raise Syntax:snthex
                    pass
            elif s[i+1] == u'.':        # 2 digit hex code
                if (i + 3 >= len(s) and
                    s[i+2] in hexdigits and
                    s[i+3] in hexdigits):
                    replacements.append(        # int expects str (not unicode)
                        (i, i+4, unichr(int(str(s[i+2:i+4]), 16))))
                else:
                    # TODO Raise Syntax:sntoct2
                    pass
            elif s[i+1] == u'[':        # longname
                for j in range(i+2, len(s)):
                    if s[j] == u']':
                        # MMA9 behaviour is \[] -> \\[]
                        longname = s[i+2:j]
                        char = named_characters.get(longname, None)
                        if longname == u'':
                            # MMA9 behaviour is \[] -> \\[]
                            replacements.append((i+1, j+1, u'\\\\[]'))
                        elif char is not None:
                            replacements.append((i, j+1, char))
                        else:
                            # TODO Raise Syntax:sntufn
                            pass
                        break

    # Make the replacements
    for start, stop, rep in reversed(replacements):
        s = s[:start] + rep + s[stop:]
    return s

class TranslateError(Exception):
    pass


class ScanError(TranslateError):
    def __init__(self, pos, text):
        TranslateError.__init__(self)
        self.pos = pos
        self.text = text

    def __unicode__(self):
        return u"Lexical error at position {0} in '{1}'.".format(
            self.pos, self.text)


class InvalidCharError(TranslateError):
    def __init__(self, char):
        TranslateError.__init__(self)
        self.char = char

    def __unicode__(self):
        return u"Invalid character at '%s'." % self.char  # .decode('utf-8')


class ParseError(TranslateError):
    def __init__(self, token):
        TranslateError.__init__(self)
        self.token = token

    def __unicode__(self):
        return u"Parse error at or near token %s." % str(self.token)

prefix_operators = {
    'Del': ['Del'],
    'Square': ['Square'],
    'ForAll': ['ForAll'],
    'Exists': ['Exists'],
    'NotExists': ['NotExists'],
}

infix_operators = {
    'PatternTest': ['PatternTest'],
    'Apply': ['Apply1'],
    'Map': ['Map'],
    'MapAll': ['MapAll'],
    'PlusMinus': ['PlusMinus'],
    'MinusPlus': ['MinusPlus'],
    'RightTee': ['RightTee'],
    'DoubleRightTee': ['DoubleRightTee'],
    'Power': ['Power'],
    'LeftTee': ['LeftTee'],
    'DoubleLeftTee': ['DoubleLeftTee'],
    'Implies': ['Implies'],
    'SuchThat': ['SuchThat'],
    'Condition': ['Condition'],
    'Rule': ['op_Rule', 'Rule'],
    'RuleDelayed': ['op_RuleDelayed', 'RuleDelayed'],
    'ReplaceAll': ['ReplaceAll'],
    'ReplaceRepeated': ['ReplaceRepeated'],
    'AddTo': ['AddTo'],
    'SubtractFrom': ['SubtractFrom'],
    'TimesBy': ['TimesBy'],
    'DivideBy': ['DivideBy'],
    'Therefore': ['Therefore'],
    'Because': ['Because'],
    'UpSet': ['UpSet'],
    'UpSetDelayed': ['UpSetDelayed'],
}

flat_infix_operators = {
    'StringJoin': ['StringJoin'],
    'SmallCircle': ['SmallCircle'],
    'CircleDot': ['CircleDot'],
    'NonCommutativeMultiply': ['NonCommutativeMultiply'],
    'Cross': ['Cross'],
    'Dot': ['RawDot'],
    'Plus': ['Plus'],
    'Intersection': ['Intersection'],
    'Union': ['Union'],
    'Diamond': ['Diamond'],
    'Wedge': ['Wedge'],
    'Vee': ['Vee'],
    'CircleTimes': ['CircleTimes'],
    'CirclePlus': ['CirclePlus'],
    'CircleMinus': ['CircleMinus'],
    'CenterDot': ['CenterDot'],
    'VerticalTilde': ['VerticalTilde'],
    'Coproduct': ['Coproduct'],
    'Cap': ['Cap'],
    'Cup': ['Cup'],
    'Star': ['Star'],
    'Backslash': ['RawBackslash'],
    'VerticalBar': ['VerticalBar'],
    'NotVerticalBar': ['NotVerticalBar'],
    'DoubleVerticalBar': ['DoubleVerticalBar'],
    'NotDoubleVerticalBar': ['NotDoubleVerticalBar'],
    'SameQ': ['SameQ'],
    'UnsameQ': ['UnsameQ'],
    'Element': ['Element'],
    'NotElement': ['NotElement'],
    'Subset': ['Subset'],
    'Superset': ['Superset'],
    'And': ['And', 'op_And'],
    'Nand': ['Nand'],
    'Xor': ['Xor'],
    'Xnor': ['Xnor'],
    'Or': ['op_Or', 'Or'],
    'Nor': ['Nor'],
    'Equivalent': ['Equivalent'],
    'Alternatives': ['Alternatives'],
    'StringExpression': ['StringExpression'],
    'Colon': ['Colon'],
    'VerticalSeparator': ['VerticalSeparator'],
}

postfix_operators = {
    'Increment': ['Increment'],
    'Decrement': ['Decrement'],
    'Factorial': ['Factorial'],
    'Factorial2': ['Factorial2'],
    'Conjugate': ['Conjugate'],
    'Transpose': ['Transpose'],
    'ConjugateTranspose': ['ConjugateTranspose', 'HermitianConjugate'],
    'Repeated': ['Repeated'],
    'RepeatedNull': ['RepeatedNull'],
    'Function': ['RawAmpersand'],
}

inequality_operators = {
    'Equal': ['op_Equal', 'LongEqual', 'Equal'],
    'Unequal': ['op_Unequal', 'NotEqual'],
    'Greater': ['Greater'],
    'Less': ['Less'],
    'GreaterEqual': ['op_GreaterEqual', 'GreaterEqual', 'GreaterSlantEqual'],
    'LessEqual': ['op_LessEqual', 'LessEqual', 'LessSlantEqual'],
}

all_operator_names = (prefix_operators.keys() + infix_operators.keys() +
                      flat_infix_operators.keys() + postfix_operators.keys() +
                      inequality_operators.keys())

precedence = (
    ('right', ['FormBox']),
    ('left', ['Semicolon']),                  # flat - custom
    ('left', ['Put', 'PutAppend']),
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
    ('right', ['Not']),
    ('right', ['ForAll', 'Exists', 'NotExists']),
    ('left', ['Element', 'NotElement', 'Subset', 'Superset']),    # flat
    ('left', ['SameQ', 'UnsameQ']),           # flat
    ('left', ['Equal', 'op_Equal', 'LongEqual', 'op_Unequal', 'NotEqual',
              'Greater', 'Less', 'GreaterEqual', 'op_GreaterEqual', 'GreaterSlantEqual',
              'LessEqual', 'op_LessEqual', 'LessSlantEqual', 'VerticalBar',
              'NotVerticalBar', 'DoubleVerticalBar', 'NotDoubleVerticalBar']),
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
    ('nonassoc', ['Get']),
    # ('nonassoc', ['blanks', 'blankdefault']),
    # ('nonassoc', ['out']),
    # ('nonassoc', ['slotsingle', 'slotseq']),
    ('nonassoc', ['MessageName']),
    # ('nonassoc', ['string']),
    # ('nonassoc', ['symbol']),
    # ('nonassoc', ['number']),
)

pg = ParserGenerator(
    [token[0] for token in tokens],
    precedence=precedence,
    cache_id="mathics",
    cache_dir="/home/angus/rmathics/rmathics/")

@pg.production('main : expr')
@pg.production('main : ')
def main(definitions, p):
    if len(p) == 0:
        return None
    elif len(p) == 1:
        return p[0]

@pg.production('expr : number')
def number(definitions, p):
    return str_to_num(p[0].getstr())

@pg.production('expr : string')
def string(definitions, p):
    s = p[0].getstr()[1:-1]
    return String(string_escape(s))

@pg.production('expr : slotseq_1')
@pg.production('expr : slotseq_2')
def slotseq(definitions, p):
    s = p[0].getstr()
    value = 1 if len(s) == 2 else int(s[2:])
    return Expression(Symbol('System`SlotSequence'), value)

@pg.production('expr : slotsingle_1')
@pg.production('expr : slotsingle_2')
def slotsingle(definitions, p):
    s = p[0].getstr()
    value = 1 if len(s) == 1 else int(s[1:])
    return Expression(Symbol('System`Slot'), value)

@pg.production('expr : out_1')
def out_1(definitions, p):
    s = p[0].getstr()
    value = int(p[0].getstr()[1:])
    if value == -1:
        return Expresion('Out')
    else:
        return Expression(Symbol('System`Out'), Integer(value))

@pg.production('expr : out_2')
def out_2(definitions, p):
    s = p[0].getstr()
    value = -len(s)
    if value == -1:
        return Expression(Symbol('System`Out'))
    else:
        return Expression(Symbol('System`Out'), Integer(value))

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

for prefix_op in prefix_operators:
    code = """def %s_prefix(definitions, p):
    return Expression(Symbol('System`%s'), p[1])""" % (prefix_op, prefix_op)
    for token in prefix_operators[prefix_op]:
        code = ("@pg.production('expr : %s expr')\n" % token) + code
    exec code

for infix_op in infix_operators:
    code = """def %s_infix(definitions, p):
    return Expression(Symbol('System`%s'), p[0], p[2])""" % (infix_op, infix_op)
    for token in infix_operators[infix_op]:
        code = ("@pg.production('expr : expr %s expr')\n" % token) + code
    exec code

for flat_infix_op in flat_infix_operators:
    code = """def %s_flat_infix(definitions, p):
    args = []
    if p[0].head.same(Symbol('System`%s')):
        args.extend(p[0].leaves)
    else:
        args.append(p[0])
    if p[2].head.same(Symbol('System`%s')):
        args.extend(p[2].leaves)
    else:
        args.append(p[2])
    return Expression(Symbol('System`%s'), *args)""" % (flat_infix_op, flat_infix_op, flat_infix_op, flat_infix_op)
    for token in flat_infix_operators[flat_infix_op]:
        code = ("@pg.production('expr : expr %s expr')\n" % token) + code
    exec code

for postfix_op in postfix_operators:
    code = """def %s_postfix(definitions, p):
    return Expression(Symbol('System`%s'), p[0])""" % (postfix_op, postfix_op)
    for token in postfix_operators[postfix_op]:
        code = ("@pg.production('expr : expr %s')\n" % token) + code
    exec code

for ineq_op in inequality_operators:
    code = """def %s_inequality(definitions, p):
        head = p[0].head
        ineq_op = ensure_context('%s')
        if head.same(Symbol(ineq_op)):
            p[0].leaves.append(p[2])
            return p[0]
        elif head.same(Symbol('System`Inequality')):
            p[0].leaves.append(Symbol(ineq_op))
            p[0].leaves.append(p[2])
            return p[0]
        elif head.name in [ensure_context(k)
                      for k in inequality_operators.keys()]:
            leaves = []
            for i, leaf in enumerate(p[0].leaves):
                if i != 0:
                    leaves.append(head)
                leaves.append(leaf)
            leaves.append(Symbol(ineq_op))
            leaves.append(p[0])
            return Expression(Symbol('System`Inequality'), *leaves)
        else:
            return Expression(Symbol(ineq_op), p[0], p[2])""" % (ineq_op, ineq_op)
    for token in inequality_operators[ineq_op]:
        code = ("@pg.production('expr : expr %s expr')\n" % token) + code
    exec code

@pg.error
def error_handler(token):
    sourcepos = token.getsourcepos()
    print token.gettokentype()
    if sourcepos is not None:
        if sourcepos.idx == 0:
            # TODO raise: Syntax:sntxb
            pass
        else:
            # TODO raise: Syntax:sntxf
            pass
    raise ParseError(token.gettokentype())

@pg.production('expr : RawLeftParenthesis expr RawRightParenthesis')
def parenthesis(definitions, p):
    expr = p[1]
    expr.parenthesized = True
    return expr

@pg.production('expr : expr args', precedence='PART')
def call(definitions, p):
    expr = Expression(p[0], *p[1])
    expr.parenthesized = True  # to handle e.g. Power[a,b]^c correctly
    return expr

@pg.production('expr : expr position', precedence='PART')
def part(definitions, p):
    expr = Expression(Symbol('System`Part'), *p[1])
    expr.parenthesized = True  # to handle e.g. Power[a,b]^c correctly
    return expr

@pg.production('args : RawLeftBracket sequence RawRightBracket')
def args(definitions, p):
    return p[1]

@pg.production('expr : RawLeftBrace sequence RawRightBrace')
def list(definitions, p):
    return Expression(Symbol('System`List'), *p[1])

@pg.production('position : RawLeftBracket RawLeftBracket sequence RawRightBracket RawRightBracket')
def position(definitions, p):
    return p[2]

@pg.production('sequence :')
@pg.production('sequence : expr')
@pg.production('sequence : sequence RawComma sequence')
def sequence(definitions, p):
    if len(p) == 0:
        return []
    elif len(p) == 1:
        return [p[0]]
    elif len(p) == 3:
        if p[0] == []:
            # TODO Raise Syntax::com
            p[0] = [Symbol('Null')]
        if p[2] == []:
            # TODO Raise Syntax::com
            p[2] = [Symbol('Null')]
        return p[0] + p[2]

@pg.production('expr : symbol')
def symbol(definitions, p):
    name = p[0].getstr()
    return Symbol(definitions.lookup_name(name))

@pg.production('pattern : blanks')
def blanks(definitions, p):
    pieces = p[0].getstr().split('_')
    count = len(pieces) - 1
    if count == 1:
        name = 'System`Blank'
    elif count == 2:
        name = 'System`BlankSequence'
    elif count == 3:
        name = 'System`BlankNullSequence'
    if pieces[-1]:
        blank = Expression(Symbol(ensure_context(name)), self.user_symbol(pieces[-1]))
    else:
        blank = Expression(Symbol(ensure_context(name)))
    if pieces[0]:
        return Expression(Symbol('System`Pattern'), Symbol(pieces[0]), blank)
    else:
        return blank

@pg.production('pattern : blankdefault')
def blankdefault(definitions, p):
    name = p[0][:-2]
    if name:
        return Expression(Symbol('System`Optional'), Expression(
            'Pattern', self.user_symbol(name), Expression(Symbol('System`Blank'))))
    else:
        return Expression(Symbol('System`Optional'), Expression(Symbol('System`Blank')))

@pg.production('expr : pattern')
def pattern(definitions, p):
    return p[0]

# def p_Get(self, args):
#     'expr : Get filename'
#     args[0] = Expression(Symbol('System`Get'), args[2])

@pg.production('expr : expr MessageName string MessageName string')
@pg.production('expr : expr MessageName symbol MessageName string')
@pg.production('expr : expr MessageName symbol')
@pg.production('expr : expr MessageName string')
def MessageName(definitions, p):
    if len(p) == 4:
        return Expression(Symbol('System`MessageName'), p[0], String(p[2]))
    elif len(p) == 6:
        return Expression(Symbol('System`MessageName'), p[0], String(p[2]), String(p[4]))

@pg.production('expr : Increment expr', precedence='PreIncrement')
def PreIncrement(definitions, p):
    return Expression(Symbol('System`PreIncrement'), p[1])

@pg.production('expr : Decrement expr', precedence='PreDecrement')
def PreDecrement(definitions, p):
    return Expression(Symbol('System`PreDecrement'), p[1])

@pg.production('expr : expr Prefix expr')
def Prefix(definitions, p):
    return Expression(p[0], p[2])

@pg.production('expr : expr Infix expr Infix expr')
def p_Infix(definitions, p):
    return Expression(p[2], p[0], p[4])

@pg.production('expr : expr Apply2 expr')
def p_Apply2(definitions, p):
    return Expression(Symbol('System`Apply'), p[0], p[2], Expression(Symbol('System`List'), Integer(1)))

@pg.production('expr : expr Derivative')
def Derivative(definitions, p):
    n = len(p[1].getstr())
    if (isinstance(p[0], Expression) and
        isinstance(p[0].head, Expression) and
        p[0].head.same(Symbol('System`Derivative')) and
        p[0].head.leaves[0].get_int_value() is not None):
        n += p[0].head.leaves[0].get_int_value()
        p[0] = p[0].leaves[0]
    return Expression(Expression(Symbol('System`Derivative'), Integer(n)), p[0])

@pg.production('expr : Integral expr DifferentialD expr', precedence='Integral')
def Integrate(definitions, p):
    return Expression(Symbol('System`Integrate'), p[1], p[3])

@pg.production('expr : expr Minus expr')
def Minus(definitions, p):
    return Expression(Symbol('System`Plus'), p[0], Expression(Symbol('System`Times'), Integer(-1), p[2]))

@pg.production('expr : Plus expr', precedence='UPlus')
def UPlus(definitions, p):
    return p[1]

@pg.production('expr : Minus expr', precedence='UMinus')
def UMinus(definitions, p):
    # if isinstance(p[0], (Integer, Real)):
    # TODO
    return Expression(Symbol('System`Times'), Integer(-1), p[1])

@pg.production('expr : PlusMinus expr', precedence='UPlusMinus')
def UPlusMinus(definitions, p):
    return Expression(Symbol('System`PlusMinus'), p[1])

@pg.production('expr : MinusPlus expr', precedence='UMinusPlus')
def UMinusPlus(definitions, p):
    return Expression(Symbol('System`MinusPlus'), p[1])

@pg.production('expr : expr RawSlash expr')
@pg.production('expr : expr Divide expr')
def Divide(definitions, p):
    return Expression(Symbol('System`Times'), p[0], Expression(Symbol('System`Power'), p[2], Integer(-1)))

@pg.production('expr : expr Times expr')
@pg.production('expr : expr RawStar expr')
@pg.production('expr : expr expr', precedence='Times')
def Times(definitions, p):
    if len(p) == 2:
        arg1, arg2 = p[0], p[1]
    elif len(p) == 3:
        arg1, arg2 = p[0], p[2]

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
    return Expression(Symbol('System`Times'), *args)

@pg.production('expr :      Span')
@pg.production('expr :      Span expr')
@pg.production('expr : expr Span')
@pg.production('expr : expr Span expr')
@pg.production('expr :      Span      Span expr')
@pg.production('expr :      Span expr Span expr')
@pg.production('expr : expr Span      Span expr')
@pg.production('expr : expr Span expr Span expr')
def Span(definitions, p):
    if len(p) == 5:
        return Expression(Symbol('System`Span'), p[0], p[2], p[4])
    elif len(p) == 4:
        if isinstance(p[0], BaseExpression):
            return Expression(Symbol('System`Span'), p[0], Symbol('All'), p[3])
        elif isinstance(p[1], BaseExpression):
            return Expression(Symbol('System`Span'), Integer(1), p[1], p[3])
    elif len(p) == 3:
        if isinstance(p[0], BaseExpression):
            return Expression(Symbol('System`Span'), p[0], p[2])
        else:
            return Expression(Symbol('System`Span'), Integer(1), Symbol('All'), p[2])
    elif len(p) == 2:
        if isinstance(p[0], BaseExpression):
            return Expression(Symbol('System`Span'), args[1], Symbol('All'))
        elif isinstance(p[1], BaseExpression):
            return Expression(Symbol('System`Span'), Integer(1), p[1])
    elif len(p) == 1:
            return Expression(Symbol('System`Span'), Integer(1), Symbol('All'))

@pg.production('expr : Not expr')
@pg.production('expr : Factorial2 expr', precedence='Not')
@pg.production('expr : Factorial expr', precedence='Not')
def Not(definitions, p):
    if p[0].getstr() == '!!':
        return Expression(Symbol('System`Not'), Expression(Symbol('System`Not'), p[1]))
    else:
        return Expression(Symbol('System`Not'), p[1])

@pg.production('expr : symbol RawColon pattern RawColon expr')
@pg.production('expr : symbol RawColon expr')
def Pattern(definitions, p):
    if len(p) == 5:
        return Expression(
            'Optional', Expression(Symbol('System`Pattern'), p[0], p[2]), p[4])
    elif len(p) == 3:
        if p[2].head.same(Symbol('System`Pattern')):
            return Expression(
                'Optional',
                Expression(Symbol('System`Pattern'), p[0], p[2].leaves[0]),
                p[2].leaves[1])
        else:
            return Expression(Symbol('System`Pattern'), p[0], p[2])

@pg.production('expr : pattern RawColon expr')
def Optional(definitions, p):
    return Expression(Symbol('System`Optional'), p[0], p[2])

@pg.production('expr : expr Postfix expr')
def Postfix(definitions, p):
    return Expression(p[2], p[0])

@pg.production('expr : expr TagSet expr Set expr')
@pg.production('expr : expr Set expr')
def Set(definitions, p):
    if len(p) == 3:
        return Expression(Symbol('System`Set'), p[0], p[2])
    elif len(p) == 5:
        return Expression(Symbol('System`TagSet'), p[0], p[2], p[4])

@pg.production('expr : expr TagSet expr SetDelayed expr')
@pg.production('expr : expr SetDelayed expr')
def SetDelayed(definitions, p):
    if len(p) == 3:
        return Expression(Symbol('System`SetDelayed'), p[0], p[2])
    elif len(p) == 5:
        return Expression(Symbol('System`TagSetDelayed'), p[0], p[2], p[4])

@pg.production('expr : expr TagSet expr Unset')
@pg.production('expr : expr Unset')
def p_Unset(definitions, p):
    if len(p) == 2:
        return Expression(Symbol('System`Unset'), args[1])
    elif len(p) == 4:
        return Expression(Symbol('System`TagUnset'), args[1], args[3])

@pg.production('expr : expr Function expr')
def Function(definitions, p):
    return Expression(Symbol('System`Function'), Expression(Symbol('System`List'), p[0]), p[2])

# def p_Put(self, args):
#     'expr : expr Put filename'
#     args[0] = Expression(Symbol('System`Put'), args[1], args[3])
#
# def p_PutAppend(self, args):
#     'expr : expr PutAppend filename'
#     args[0] = Expression(Symbol('System`PutAppend'), args[1], args[3])

@pg.production('expr : expr Semicolon expr')
@pg.production('expr : expr Semicolon')
def Compound(definitions, p):
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

# Construct lexer
lg = LexerGenerator()
for token, regex in tokens:
    lg.add(token, regex)
lg.ignore(r'\s+|(?s)\(\*.*?\*\)')
lexer = lg.build()

# Construct parser
parser = pg.build()
parse = lambda string, definitions: parser.parse(lexer.lex(prelex(string)), state=definitions)
