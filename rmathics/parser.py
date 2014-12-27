from __future__ import unicode_literals
from rply import ParserGenerator, LexerGenerator
from rply.token import BaseBox
from math import log10

from rmathics.expression import (
    BaseExpression, Expression, Integer, Real, Symbol, String, Rational,
    ensure_context)
from rmathics.characters import letters, letterlikes, named_characters
from rmathics.convert import str_to_num

try:
    import rpython
    from rpython.annotator import model
except:
    rpython = None


# Symbols can be any letters
base_symb = r'((?![0-9])([0-9${0}{1}])+)'.format(letters, letterlikes)
full_symb = r'(`?{0}(`{0})*)'.format(base_symb)

tokens = (
    ('number', r'((\d+\^\^([a-zA-Z0-9]+\.?[a-zA-Z0-9]*|[a-zA-Z0-9]*\.?[a-zA-Z0-9]+))|(\d+\.?\d*|\d*\.?\d+))(``?(\+|-)?(\d+\.?\d*|\d*\.?\d+)|`)?(\*\^(\+|-)?\d+)?'),
    ('string', r'"([^\\"]|\\\\|\\"|\\n|\\r|\\r\\n)*"'),
    ('blankdefault', r'{0}?_\.'.format(full_symb)),
    ('blanks', r'{0}?_(__?)?{0}?'.format(full_symb)),
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
    ('Prefix', r'\@'),
    ('Infix', r'\~'),
    ('Apply1', r'\@\@'),
    ('Apply2', r'\@\@\@'),
    ('Map', r'\/\@'),
    ('MapAll', r'\/\/\@'),
    ('Factorial', r'\!'),
    ('Factorial2', r'\!\!'),
    ('Transpose', r'\uf3c7'),
    ('Conjugate', r'\uf3c8'),
    ('ConjugateTranspose', r'\uf3c9'),
    ('HermitianConjugate', r'\uf3ce'),
    ('Derivative', r'\'+'),
    ('StringJoin', r'\<\>'),
    ('Power', r'\^'),
    ('Integral', r'\u222b'),
    ('DifferentialD', r'\uf74c'),
    # (PartialD, r'\u2202'),
    ('Del', r'\u2207'),
    ('Square', r'\uf520'),
    ('SmallCircle', r'\u2218'),
    ('CircleDot', r'\u2299'),
    ('NonCommutativeMultiply', r'\*\*'),
    ('Cross', r'\uf4a0'),
    ('RawDot', r'\.'),
    ('Plus', r'\+'),
    ('Minus', r'\-'),
    ('RawSlash', r'\/'),
    ('RawBackslash', r'\\'),
    ('Diamond', r'\u22c4'),
    ('Wedge', r'\u22c0'),
    ('Vee', r'\u22c1'),
    ('CircleTimes', r'\u2297'),
    ('CenterDot', r'\u00b7'),
    ('Star', r'\u22c6'),
    # (Sum, r' \u2211'),
    # (Product, r'\u220f'),
    ('RawStar', r'\*'),
    ('Times', r'\u00d7'),
    ('Divide', r'\u00f7'),
    ('PlusMinus', r'\u00b1'),
    ('MinusPlus', r'\u2213'),
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
    ('Or', r'\u2228'),
    ('Nor', r'\u22BD'),
    ('And', r'\u2227'),
    ('Nand', r'\u22BC'),
    ('Xor', r'\u22BB'),
    ('Xnor', r'\uF4A2'),
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
    ('Colon', r'\u2236'),
    ('Postfix', r'\/\/'),
    ('Set', r'\='),
    ('SetDelayed', r'\:\='),
    ('UpSet', r'\^\='),
    ('UpSetDelayed', r'\^\:\='),
    ('TagSet', r'\/\:'),
    ('Unset', r'\=\.'),
    ('Semicolon', r'\;'),
    # (DiscreteShift, r'\uf4a3'),
    # (DiscreteRatio, r'\uf4a4'),
    # (DifferenceDelta, r'\u2206'),
    ('VerticalTilde', r'\u2240'),
    ('Coproduct', r'\u2210'),
    ('Cap', r'\u2322'),
    ('Cup', r'\u2323'),
    ('CirclePlus', r'\u2295'),
    ('CircleMinus', r'\u2296'),
    ('Intersection', r'\u22c2'),
    ('Union', r'\u22c3'),
    ('Equal', r'\uf431'),
    ('LongEqual', r'\uf7d9'),
    ('NotEqual', r'\u2260'),
    ('LessEqual', r'\u2264'),
    ('LessSlantEqual', r'\u2a7d'),
    ('GreaterEqual', r' \u2265 '),
    ('GreaterSlantEqual', r'\u2a7e'),
    ('VerticalBar', r'\u2223'),
    ('NotVerticalBar', r'\u2224'),
    ('DoubleVerticalBar', r'\u2225'),
    ('NotDoubleVerticalBar', r'\u2226'),
    ('Element', r'\u2208'),
    ('NotElement', r'\u2209'),
    ('Subset', r'\u2282'),
    ('Superset', r'\u2283'),
    ('ForAll', r'\u2200'),
    ('Exists', r'\u2203'),
    ('NotExists', r'\u2204'),
    ('Not', r'\u00AC'),
    ('Equivalent', r'\u29E6'),
    ('Implies', r'\uF523'),
    ('RightTee', r'\u22A2'),
    ('DoubleRightTee', r'\u22A8'),
    ('LeftTee', r'\u22A3'),
    ('DoubleLeftTee', r'\u2AE4'),
    ('SuchThat', r'\u220D'),
    ('Rule', r'\uF522'),
    ('RuleDelayed', r'\uF51F'),
    ('VerticalSeparator', r'\uF432'),
    ('Therefore', r'\u2234'),
    ('Because', r'\u2235'),
    ('Function', r'\uF4A1'),
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
                        (i, i+6, unichr(int(str(s[i+2:i+6]), 16))))
                else:
                    # TODO Raise Syntax:snthex
                    pass
            elif s[i+1] == '.':        # 2 digit hex code
                if (i+3 >= len(s) and
                    s[i+2] in hexdigits and
                    s[i+3] in hexdigits):
                    replacements.append(        # int expects str (not unicode)
                        (i, i+4, unichr(int(str(s[i+2:i+4]), 16))))
                else:
                    # TODO Raise Syntax:sntoct2
                    pass
            elif s[i+1] == '[':        # longname
                for j in range(i+2, len(s)):
                    if s[j] == ']':
                        # MMA9 behaviour is \[] -> \\[]
                        longname = s[i+2:j]
                        # assert isinstance(longname, unicode)
                        char = named_characters.get(longname, None)
                        if longname == '':
                            # MMA9 behaviour is \[] -> \\[]
                            replacements.append((i+1, j+1, '\\\\[]'))
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
    pass
    # def __init__(self, pos, text):
    #     TranslateError.__init__(self)
    #     self.pos = pos
    #     self.text = text

    # def __unicode__(self):
    #     return "Lexical error at position {0} in '{1}'.".format(
    #         self.pos, self.text)


class InvalidCharError(TranslateError):
    pass
    # def __init__(self, char):
    #     TranslateError.__init__(self)
    #     self.char = char

    # def __unicode__(self):
    #     return "Invalid character at '%s'." % self.char  # .decode('utf-8')


class ParseError(TranslateError):
    pass
    # def __init__(self, token):
    #     TranslateError.__init__(self)
    #     self.token = token

    # def __unicode__(self):
    #     return "Parse error at or near token %s." % str(self.token)


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

all_operator_names = (
    list(prefix_operators.keys()) +
    list(infix_operators.keys()) +
    list(flat_infix_operators.keys()) +
    list(postfix_operators.keys()) +
    list(inequality_operators.keys()))

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
    return Expression(Symbol('System`SlotSequence'), Integer(value))

@pg.production('expr : slotsingle_1')
@pg.production('expr : slotsingle_2')
def slotsingle(definitions, p):
    s = p[0].getstr()
    value = 1 if len(s) == 1 else int(s[1:])
    return Expression(Symbol('System`Slot'), Integer(value))

@pg.production('expr : out_1')
def out_1(definitions, p):
    s = p[0].getstr()
    value = int(p[0].getstr()[1:])
    if value == -1:
        return Expression(Symbol('System`Out'))
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
    exec(code)

for infix_op in infix_operators:
    code = """def %s_infix(definitions, p):
    return Expression(Symbol('System`%s'), p[0], p[2])""" % (
        infix_op, infix_op)
    for token in infix_operators[infix_op]:
        code = ("@pg.production('expr : expr %s expr')\n" % token) + code
    exec(code)

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
    expr = Expression(Symbol('System`%s'))
    expr.leaves = args
    return expr""" % (
        flat_infix_op, flat_infix_op, flat_infix_op, flat_infix_op)
    for token in flat_infix_operators[flat_infix_op]:
        code = ("@pg.production('expr : expr %s expr')\n" % token) + code
    exec(code)

for postfix_op in postfix_operators:
    code = """def %s_postfix(definitions, p):
    return Expression(Symbol('System`%s'), p[0])""" % (postfix_op, postfix_op)
    for token in postfix_operators[postfix_op]:
        code = ("@pg.production('expr : expr %s')\n" % token) + code
    exec(code)

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
            expr = Expression(Symbol('System`Inequality'))
            expr.leaves = leaves
            return expr
        else:
            return Expression(Symbol(ineq_op), p[0], p[2])""" % (
        ineq_op, ineq_op)
    for token in inequality_operators[ineq_op]:
        code = ("@pg.production('expr : expr %s expr')\n" % token) + code
    exec(code)

@pg.error
def error_handler(definitions, token):
    sourcepos = token.getsourcepos()
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

class SequenceBox(BaseBox):
    def __init__(self, leaves):
        self.leaves = leaves

@pg.production('expr : expr args', precedence='PART')
def call(definitions, p):
    expr = Expression(p[0])
    expr.leaves = p[1].leaves
    expr.parenthesized = True  # to handle e.g. Power[a,b]^c correctly
    return expr

@pg.production('expr : expr position', precedence='PART')
def part(definitions, p):
    expr = Expression(Symbol('System`Part'))
    expr.leaves = p[1].leaves
    expr.parenthesized = True  # to handle e.g. Power[a,b]^c correctly
    return expr

@pg.production('args : RawLeftBracket sequence RawRightBracket')
def args(definitions, p):
    return p[1]

@pg.production('expr : RawLeftBrace sequence RawRightBrace')
def list(definitions, p):
    expr = Expression(Symbol('System`List'))
    expr.leaves = p[1].leaves
    return expr

@pg.production('position : RawLeftBracket RawLeftBracket sequence RawRightBracket RawRightBracket')
def position(definitions, p):
    return p[2]

@pg.production('sequence :')
@pg.production('sequence : expr')
@pg.production('sequence : sequence RawComma sequence')
def sequence(definitions, p):
    assert len(p) in (0, 1, 3)
    if len(p) == 0:
        return SequenceBox([])
    elif len(p) == 1:
        return SequenceBox([p[0]])
    elif len(p) == 3:
        if p[0].leaves == 0:
            # TODO Raise Syntax::com
            p[0].leaves = [Symbol('Null')]
        if p[2].leaves == []:
            # TODO Raise Syntax::com
            p[2].leaves = [Symbol('Null')]
        return SequenceBox(p[0].leaves + p[2].leaves)
    else:
        raise ValueError

@pg.production('expr : symbol')
def symbol(definitions, p):
    name = p[0].getstr()
    return Symbol(definitions.lookup_name(name))

@pg.production('pattern : blanks')
def blanks(definitions, p):
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
        blank = Expression(Symbol(ensure_context(name)), Symbol(definitions.lookup_name(pieces[-1])))
    else:
        blank = Expression(Symbol(ensure_context(name)))
    if pieces[0]:
        return Expression(Symbol('System`Pattern'), Symbol(pieces[0]), blank)
    else:
        return blank

@pg.production('pattern : blankdefault')
def blankdefault(definitions, p):
    assert isinstance(p[0], unicode) and len(p[0]) >= 2
    name = p[0][:-2]
    if name:
        return Expression(Symbol('System`Optional'), Expression(
            Symbol('System`Pattern'), Symbol(definitions.lookup_name(name)), Expression(Symbol('System`Blank'))))
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
    assert len(p) in (3, 5)
    p2 = p[2].getstr()
    if p2[0] == '"':
        p2 = String(p2[1:-1])
    else:
        p2 = Symbol(p2)
    if len(p) == 3:
        return Expression(Symbol('System`MessageName'), p[0], p2)
    elif len(p) == 5:
        p4 = p[4].getstr()
        if p4[0] == '"':
            p4 = String(p4[1:-1])
        else:
            p4 = Symbol(p4)
        return Expression(Symbol('System`MessageName'), p[0], p2, p4)

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
    return Expression(
        Symbol('System`Apply'), p[0], p[2],
        Expression(Symbol('System`List'), Integer(1)))

@pg.production('expr : expr Derivative')
def Derivative(definitions, p):
    n = len(p[1].getstr())
    is_derivative = (isinstance(p[0], Expression) and
                     p[0].head.same(Symbol('System`Derivative')) and
                     isinstance(p[0].head.leaves[0], Integer))
    if isinstance(p[0].head, Expression) and p[0].head.head.same(Symbol('System`Derivative')):
        head = p[0].head
        leaves = p[0].leaves
        if len(head.leaves) == 1 and isinstance(head.leaves[0], Integer) and len(leaves) == 1:
            n += head.leaves[0].getint()
            p[0] = leaves[0]
    return Expression(
        Expression(Symbol('System`Derivative'), Integer(n)), p[0])

@pg.production('expr : Integral expr DifferentialD expr',
               precedence='Integral')
def Integrate(definitions, p):
    return Expression(Symbol('System`Integrate'), p[1], p[3])

@pg.production('expr : expr Minus expr')
def Minus(definitions, p):
    return Expression(Symbol('System`Plus'), p[0],
                      Expression(Symbol('System`Times'), Integer(-1), p[2]))

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
    return Expression(Symbol('System`Times'), p[0],
                      Expression(Symbol('System`Power'), p[2], Integer(-1)))

@pg.production('expr : expr Times expr')
@pg.production('expr : expr RawStar expr')
@pg.production('expr : expr expr', precedence='Times')
def Times(definitions, p):
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
            return Expression(Symbol('System`Span'), Integer(1),
                              Symbol('System`All'), p[2])
    elif len(p) == 2:
        if isinstance(p[0], BaseExpression):
            return Expression(Symbol('System`Span'), p[1], Symbol('All'))
        elif isinstance(p[1], BaseExpression):
            return Expression(Symbol('System`Span'), Integer(1), p[1])
    elif len(p) == 1:
            return Expression(Symbol('System`Span'), Integer(1), Symbol('All'))

@pg.production('expr : Not expr')
@pg.production('expr : Factorial2 expr', precedence='Not')
@pg.production('expr : Factorial expr', precedence='Not')
def Not(definitions, p):
    if p[0].getstr() == '!!':
        return Expression(
            Symbol('System`Not'), Expression(Symbol('System`Not'), p[1]))
    else:
        return Expression(Symbol('System`Not'), p[1])

@pg.production('expr : symbol RawColon pattern RawColon expr')
@pg.production('expr : symbol RawColon expr')
def Pattern(definitions, p):
    if len(p) == 5:
        return Expression(
            Symbol('System`Optional'), Expression(Symbol('System`Pattern'), p[0], p[2]), p[4])
    elif len(p) == 3:
        if p[2].head.same(Symbol('System`Pattern')):
            return Expression(
                Symbol('System`Optional'),
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
        return Expression(Symbol('System`Unset'), p[0])
    elif len(p) == 4:
        return Expression(Symbol('System`TagUnset'), p[0], p[2])

@pg.production('expr : expr Function expr')
def Function(definitions, p):
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


def parse(string, definitions):
    """
    Parses a string and returns an expression (or None if the string is empty)
    """
    return parser.parse(lexer.lex(prelex(string)), state=definitions)
