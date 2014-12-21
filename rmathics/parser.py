from rply import ParserGenerator, LexerGenerator

import re
from math import log10

from rmathics.expression import (BaseExpression, Expression, Integer,
                                     Real, Symbol, String, Rational,
                                     ensure_context)
# from mathics.core.numbers import dps
from rmathics.characters import letters, letterlikes, named_characters

# from mathics.builtin.numeric import machine_precision
machine_precision = 18


# Symbols can be any letters
base_symb = ur'((?![0-9])([0-9${0}{1}])+)'.format(letters, letterlikes)
full_symb = ur'(`?{0}(`{0})*)'.format(base_symb)

# symbol_re = re.compile(full_symb)


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
                    #TODO Raise Syntax:snthex
                    pass
            elif s[i+1] == u'.':        # 2 digit hex code
                if (i + 3 >= len(s) and
                    s[i+2] in hexdigits and
                    s[i+3] in hexdigits):
                    replacements.append(        # int expects str (not unicode)
                        (i, i+4, unichr(int(str(s[i+2:i+4]), 16))))
                else:
                    #TODO Raise Syntax:sntoct2
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


# def is_symbol_name(text):
#     return symbol_re.sub('', text) == ''

prefix_operators = {
    'Del': 'Del',
    'Square': 'Square',
    'ForAll': 'ForAll',
    'Exists': 'Exists',
    'NotExists': 'NotExists',
}

infix_operators = {
    'PatternTest': 'PatternTest',
    'Apply': 'Apply1',
    'Map': 'Map',
    'MapAll': 'MapAll',
    'PlusMinus': 'PlusMinus',
    'MinusPlus': 'MinusPlus',
    'RightTee': 'RightTee',
    'DoubleRightTee': 'DoubleRightTee',
    'Power': 'Power',
    'LeftTee': 'LeftTee',
    'DoubleLeftTee': 'DoubleLeftTee',
    'Implies': 'Implies',
    'SuchThat': 'SuchThat',
    'Condition': 'Condition',
    'Rule': ['op_Rule', 'Rule'],
    'RuleDelayed': ['op_RuleDelayed', 'RuleDelayed'],
    'ReplaceAll': 'ReplaceAll',
    'ReplaceRepeated': 'ReplaceRepeated',
    'AddTo': 'AddTo',
    'SubtractFrom': 'SubtractFrom',
    'TimesBy': 'TimesBy',
    'DivideBy': 'DivideBy',
    'Therefore': 'Therefore',
    'Because': 'Because',
    'UpSet': 'UpSet',
    'UpSetDelayed': 'UpSetDelayed',
}

flat_infix_operators = {
    'StringJoin': 'StringJoin',
    'SmallCircle': 'SmallCircle',
    'CircleDot': 'CircleDot',
    'NonCommutativeMultiply': 'NonCommutativeMultiply',
    'Cross': 'Cross',
    'Dot': 'RawDot',
    'Plus': 'Plus',
    'Intersection': 'Intersection',
    'Union': 'Union',
    'Diamond': 'Diamond',
    'Wedge': 'Wedge',
    'Vee': 'Vee',
    'CircleTimes': 'CircleTimes',
    'CirclePlus': 'CirclePlus',
    'CircleMinus': 'CircleMinus',
    'CenterDot': 'CenterDot',
    'VerticalTilde': 'VerticalTilde',
    'Coproduct': 'Coproduct',
    'Cap': 'Cap',
    'Cup': 'Cup',
    'Star': 'Star',
    'Backslash': 'RawBackslash',
    'VerticalBar': 'VerticalBar',
    'NotVerticalBar': 'NotVerticalBar',
    'DoubleVerticalBar': 'DoubleVerticalBar',
    'NotDoubleVerticalBar': 'NotDoubleVerticalBar',
    'SameQ': 'SameQ',
    'UnsameQ': 'UnsameQ',
    'Element': 'Element',
    'NotElement': 'NotElement',
    'Subset': 'Subset',
    'Superset': 'Superset',
    'And': ['And', 'op_And'],
    'Nand': 'Nand',
    'Xor': 'Xor',
    'Xnor': 'Xnor',
    'Or': ['op_Or', 'Or'],
    'Nor': 'Nor',
    'Equivalent': 'Equivalent',
    'Alternatives': 'Alternatives',
    'StringExpression': 'StringExpression',
    'Colon': 'Colon',
    'VerticalSeparator': 'VerticalSeparator',
}

postfix_operators = {
    'Increment': 'Increment',
    'Decrement': 'Decrement',
    'Factorial': 'Factorial',
    'Factorial2': 'Factorial2',
    'Conjugate': 'Conjugate',
    'Transpose': 'Transpose',
    'ConjugateTranspose': ['ConjugateTranspose', 'HermitianConjugate'],
    'Repeated': 'Repeated',
    'RepeatedNull': 'RepeatedNull',
    'Function': 'RawAmpersand',
}

innequality_operators = {
    'Equal': ['op_Equal', 'LongEqual', 'Equal'],
    'Unequal': ['op_Unequal', 'NotEqual'],
    'Greater': 'Greater',
    'Less': 'Less',
    'GreaterEqual': ['op_GreaterEqual', 'GreaterEqual', 'GreaterSlantEqual'],
    'LessEqual': ['op_LessEqual', 'LessEqual', 'LessSlantEqual'],
}

all_operator_names = (prefix_operators.keys() + infix_operators.keys() +
                      flat_infix_operators.keys() + postfix_operators.keys() +
                      innequality_operators.keys())

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
    #('left', ['Sum']),                       # flat
    ('left', ['CirclePlus', 'CircleMinus']),  # flat
    ('left', ['Cap', 'Cup']),                 # flat
    ('left', ['Coproduct']),                  # flat
    ('left', ['VerticalTilde']),              # flat
    #('left', ['Product']),
    ('left', ['Star']),                       # flat
    # This is a hack to get implicit times working properly:
    ('left', ['Times', 'RawStar', 'blanks', 'blankdefault', 'out',
              'slotsingle1', 'slotsingle2', 'slotseq1', 'slotseq2',
               'string', 'symbol', 'number', 'RawLeftBrace',
               'RawLeftParenthesis']),  # flat,
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
    #('nonassoc', ['blanks', 'blankdefault']),
    #('nonassoc', ['out']),
    #('nonassoc', ['slotsingle', 'slotseq']),
    ('nonassoc', ['MessageName']),
    #('nonassoc', ['string']),
    #('nonassoc', ['symbol']),
    #('nonassoc', ['number']),
)

pg = ParserGenerator(
    [token[0] for token in tokens],
    precedence=precedence,
    cache_id="mathics")

@pg.production('main : expr')
@pg.production('main : ')
def main(p):
    if len(p) == 0:
        return None
    elif len(p) == 1:
        return p[0]


@pg.production('expr : number')
def number(p):
    """
    NOT_RPYTHON
    """
    s = p[0].getstr()
    # Look for base
    s = s.split('^^')
    if len(s) == 1:
        base, s = 10, s[0]
    else:
        assert len(s) == 2
        base, s = int(s[0]), s[1]
        assert 2 <= base <= 36

    # Look for mantissa
    s = s.split('*^')
    if len(s) == 1:
        n, s = 0, s[0]
    else:
        # TODO: modify regex and provide error message if n not an int
        n, s = int(s[1]), s[0]

    # Look at precision ` suffix to get precision/accuracy
    prec, acc = None, None
    s = s.split('`', 1)
    if len(s) == 1:
        suffix, s = None, s[0]
    else:
        suffix, s = s[1], s[0]

        if suffix == '':
            prec = machine_precision
        elif suffix.startswith('`'):
            acc = float(suffix[1:])
        else:
            if re.match('0+$', s) is not None:
                return Integer(0)
            prec = float(suffix)

    # Look for decimal point
    if s.count('.') == 0:
        if suffix is None:
            if n < 0:
                return Rational(int(s, base), base ** abs(n))
            else:
                return Integer(int(s, base) * (base ** n))
        else:
            s = s + '.'

    if base == 10:
        if n != 0:
            s = s + 'E' + str(n)    # sympy handles this

        if acc is not None:
            if float(s) == 0:
                prec = 0.
            else:
                prec = acc + log10(float(s)) + n

        # XXX
        if prec is not None:
            prec = dps(prec)
        return Real(s)  # FIXME
        # return Real(s, prec)
        # return Real(s, prec, acc)
    else:
        # Convert the base
        assert isinstance(base, int) and 2 <= base <= 36

        # Put into standard form mantissa * base ^ n
        s = s.split('.')
        if len(s) == 1:
            man = s[0]
        else:
            n -= len(s[1])
            man = s[0] + s[1]

        man = int(man, base)

        if n >= 0:
            result = Integer(man * base ** n)
        else:
            result = Rational(man, base ** -n)

        if acc is None and prec is None:
            acc = len(s[1])
            acc10 = acc * log10(base)
            prec10 = acc10 + log10(result.to_python())
            if prec10 < 18:
                prec10 = None
        elif acc is not None:
            acc10 = acc * log10(base)
            prec10 = acc10 + log10(result.to_python())
        elif prec is not None:
            if prec == machine_precision:
                prec10 = machine_precision
            else:
                prec10 = prec * log10(base)
        # XXX
        if prec10 is None:
            prec10 = machine_precision
        else:
            prec10 = dps(prec10)
        return result.round(prec10)

@pg.production('expr : string')
def string(p):
    s = p[0].getstr()[1:-1]
    return String(string_escape(s))

@pg.production('expr : slotseq_1')
@pg.production('expr : slotseq_2')
def slotseq(p):
    s = p[0].getstr()
    value = 1 if len(s) == 2 else int(s[2:])
    return Expression('SlotSequence', value)

@pg.production('expr : slotsingle_1')
@pg.production('expr : slotsingle_2')
def slotsingle(p):
    s = p[0].getstr()
    value = 1 if len(s) == 1 else int(s[1:])
    return Expression('Slot', value)

@pg.production('expr : out_1')
def out_1(p):
    s = p[0].getstr()
    value = int(p[0].getstr()[1:])
    if value == -1:
        return Expresion('Out')
    else:
        return Expression('Out', Integer(value))

@pg.production('expr : out_2')
def out_2(p):
    s = p[0].getstr()
    value = -len(s)
    if value == -1:
        return Expresion('Out')
    else:
        return Expression('Out', Integer(value))

##     def t_PutAppend(self, t):
##         r' \>\>\> '
##         t.lexer.begin('file')
##         return t
##
##     def t_Put(self, t):
##         r' \>\> '
##         t.lexer.begin('file')
##         return t
##
##     def t_Get(self, t):
##         r' \<\< '
##         t.lexer.begin('file')
##         return t
##
##     def t_file_filename(self, t):
##         r'''
##         (?P<quote>\"?)                              (?# Opening quotation mark)
##             [a-zA-Z0-9\`/\.\\\!\-\:\_\$\*\~\?]+     (?# Literal characters)
##         (?P=quote)                                  (?# Closing quotation mark)
##         '''
##         s = t.value
##         if s.startswith('"'):
##             s = s[1:-1]
##         s = self.string_escape(s)
##         s = s.replace('\\', '\\\\')
##         t.value = String(s)
##         t.lexer.begin('INITIAL')
##         return t
##
##     def __init__(self):
##         for prefix_op in prefix_operators:
##             @ONEARG
##             def tmp(args, op=prefix_op):
##                 args[0] = Expression(op, args[2])
##             tokens = prefix_operators[prefix_op]
##             if not isinstance(tokens, list):
##                 tokens = [tokens]
##             tmp.__doc__ = 'expr : ' + '\n     | '.join(
##                 ['{0} expr'.format(token) for token in tokens])
##             setattr(self, 'p_{0}_prefix'.format(prefix_op), tmp)
##
##         for infix_op in infix_operators:
##             tokens = infix_operators[infix_op]
##             if not isinstance(tokens, list):
##                 tokens = [tokens]
##
##             @ONEARG
##             def tmp(args, op=infix_op):
##                 args[0] = Expression(op, args[1], args[3])
##             tmp.__doc__ = 'expr : ' + '\n     | '.join(
##                 ['expr {0} expr'.format(token) for token in tokens])
##             setattr(self, 'p_{0}_infix'.format(infix_op), tmp)
##
##         for flat_infix_op in flat_infix_operators:
##             tokens = flat_infix_operators[flat_infix_op]
##             if not isinstance(tokens, list):
##                 tokens = [tokens]
##
##             @ONEARG
##             def tmp(args, op=flat_infix_op):
##                 op = ensure_context(op)
##                 if args[1].get_head_name() == op:
##                     args[1].leaves.append(args[3])
##                     args[0] = args[1]
##                 else:
##                     args[0] = Expression(op, args[1], args[3])
##             tmp.__doc__ = 'expr : ' + '\n     | '.join(
##                 ['expr {0} expr'.format(token) for token in tokens])
##             setattr(self, 'p_{0}_infix'.format(flat_infix_op), tmp)
##
##         for postfix_op in postfix_operators:
##             @ONEARG
##             def tmp(args, op=postfix_op):
##                 args[0] = Expression(op, args[1])
##             tokens = postfix_operators[postfix_op]
##             if not isinstance(tokens, list):
##                 tokens = [tokens]
##             tmp.__doc__ = 'expr : ' + '\n     | '.join(
##                 ['expr {0}'.format(token) for token in tokens])
##             setattr(self, 'p_{0}_postfix'.format(postfix_op), tmp)
##
##         for innequality_op in innequality_operators:
##             @ONEARG
##             def tmp(args, op=innequality_op):
##                 head = args[1].get_head_name()
##                 if head == ensure_context(op):
##                     args[1].leaves.append(args[3])
##                     args[0] = args[1]
##                 elif head == 'System`Inequality':
##                     args[1].leaves.append(Symbol(op))
##                     args[1].leaves.append(args[3])
##                     args[0] = args[1]
##                 elif head in [ensure_context(k)
##                               for k in innequality_operators.keys()]:
##                     leaves = []
##                     for i, leaf in enumerate(args[1].leaves):
##                         if i != 0:
##                             leaves.append(Symbol(head))
##                         leaves.append(leaf)
##                     leaves.append(Symbol(op))
##                     leaves.append(args[3])
##                     args[0] = Expression('Inequality', *leaves)
##                 else:
##                     args[0] = Expression(op, args[1], args[3])
##             tokens = innequality_operators[innequality_op]
##             if not isinstance(tokens, list):
##                 tokens = [tokens]
##             tmp.__doc__ = 'expr : ' + '\n     | '.join(
##                 ['expr {0} expr'.format(token) for token in tokens])
##             setattr(self, 'p_{0}_innequality'.format(innequality_op), tmp)
##
##     def build(self, **kwargs):
##         self.parser = yacc.yacc(
##             module=self,
##             debug=False,
##             tabmodule='mathics.core.parsetab',  # where to look for parsetab
##             outputdir='mathics/core/',          # where to store parsetab
##             **kwargs)
##
##     def user_symbol(self, name):
##         return Symbol(self.definitions.lookup_name(name))
##
@pg.error
def error_handler(token):
    sourcepos = token.getsourcepos()
    print token.gettokentype()
    if sourcepos.idx == 0:
        # TODO raise: Syntax:sntxb
        pass
    else:
        # TODO raise: Syntax:sntxf
        pass
    raise ParseError(token.gettokentype())

##     def p_Empty(self, args):
##         'Expression :'
##         args[0] = None

@pg.production('expr : RawLeftParenthesis expr RawRightParenthesis')
def parenthesis(p):
    expr = p[1]
    expr.parenthesized = True
    return expr

@pg.production('expr : expr args')
def call(p):
    expr = Expression(p[0], *args[1])
    expr.parenthesized = True  # to handle e.g. Power[a,b]^c correctly
    return expr

@pg.production('expr : expr position')
def part(p):
    expr = Expression('Part', *args[2])
    expr.parenthesized = True  # to handle e.g. Power[a,b]^c correctly
    return expr

@pg.production('args : RawLeftBracket sequence RawRightBracket')
def args(p):
    return p[1]

@pg.production('expr : RawLeftBrace sequence RawRightBrace')
def list(p):
    return Expression('List', *p[1])

@pg.production('position : RawLeftBracket RawLeftBracket sequence RawRightBracket RawRightBracket')
def position(p):
    return p[3]

@pg.production('sequence :')
@pg.production('sequence : expr')
@pg.production('sequence : sequence RawComma sequence')
def sequence(p):
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
def symbol(p):
    name = p[0].getstr()
    # FIXME
    # return Symbol(self.definitions.lookup_name(name))
    return Symbol(name)

@pg.production('pattern : blanks')
def blanks(p):
    pieces = p[0].getstr().split('_')
    count = len(pieces) - 1
    if count == 1:
        name = 'Blank'
    elif count == 2:
        name = 'BlankSequence'
    elif count == 3:
        name = 'BlankNullSequence'
    if pieces[-1]:
        blank = Expression(name, self.user_symbol(pieces[-1]))
    else:
        blank = Expression(name)
    if pieces[0]:
        return Expression('Pattern', self.user_symbol(pieces[0]), blank)
    else:
        return blank

@pg.production('pattern : blankdefault')
def blankdefault(p):
    name = p[0][:-2]
    if name:
        return Expression('Optional', Expression(
            'Pattern', self.user_symbol(name), Expression('Blank')))
    else:
        return Expression('Optional', Expression('Blank'))

@pg.production('expr : pattern')
def pattern(p):
    return p[0]

##def p_Get(self, args):
##    'expr : Get filename'
##    args[0] = Expression('Get', args[2])
##

@pg.production('expr : expr MessageName string MessageName string')
@pg.production('expr : expr MessageName symbol MessageName string')
@pg.production('expr : expr MessageName symbol')
@pg.production('expr : expr MessageName string')
def MessageName(p):
   if len(p) == 4:
       return Expression('MessageName', p[0], String(p[2]))
   elif len(p) == 6:
       return Expression('MessageName', p[0], String(p[2]), String(p[4]))

@pg.production('expr : Increment expr')
def PreIncrement(p):
    return Expression('PreIncrement', p[1])

@pg.production('expr : Decrement expr')
def PreDecrement(p):
    return Expression('PreDecrement', p[1])

@pg.production('expr : expr Prefix expr')
def Prefix(p):
    return Expression(p[0], p[1])

@pg.production('expr : expr Infix expr Infix expr')
def p_Infix(p):
    return Expression(p[2], p[0], p[4])

@pg.production('expr : expr Apply2 expr')
def p_Apply2(p):
    return Expression('Apply', p[0], p[2], Expression('List', Integer(1)))

@pg.production('expr : expr Derivative')
def Derivative(p):
    n = len(p[1])
    if (isinstance(p[0], Expression) and
        isinstance(p[0].head, Expression) and
        p[0].head.get_head_name() == 'System`Derivative' and
        p[0].head.leaves[0].get_int_value() is not None):
        n += p[0].head.leaves[0].get_int_value()
        p[0] = p[0].leaves[0]
    return Expression(Expression('Derivative', Integer(n)), p[0])

@pg.production('expr : Integral expr DifferentialD expr')
def Integrate(p):
    return Expression('Integrate', p[1], p[3])

@pg.production('expr : expr Minus expr')
def Minus(p):
    return Expression('Plus', p[0], Expression('Times', Integer(-1), p[2]))

@pg.production('expr : Plus expr')
def UPlus(p):
    return p[1]

@pg.production('expr : Minus expr')
def UMinus(p):
    # if p[1].get_head_name() in ['System`Integer', 'System`Real']:
    # TODO
    return Expression('Times', Integer(-1), p[1])

@pg.production('expr : PlusMinus expr')
def UPlusMinus(p):
    return Expression('PlusMinus', p[1])

@pg.production('expr : MinusPlus expr')
def UMinusPlus(p):
    return Expression('MinusPlus', p[1])

@pg.production('expr : expr RawSlash expr')
@pg.production('expr : expr Divide expr')
def Divide(p):
    return Expression('Times', p[0], Expression('Power', p[2], Integer(-1)))

@pg.production('expr : expr Times expr')
@pg.production('expr : expr RawStar expr')
@pg.production('expr : expr expr')
def p_Times(p):
    if len(p) == 2:
        arg1, arg2 = p[0], p[1]
    elif len(p) == 3:
        arg1, arg2 = p[0], p[2]

    # flatten
    args = []
    if arg1.get_head_name() == 'System`Times':
        args.extend(arg1.leaves)
    else:
        args.append(arg1)
    if arg2.get_head_name() == 'System`Times':
        args.extend(arg2.leaves)
    else:
        args.append(arg2)
    return Expression('System`Times', *args)

@pg.production('expr : expr Span expr Span expr')
@pg.production('expr : expr Span      Span expr')
@pg.production('expr :      Span expr Span expr')
@pg.production('expr :      Span      Span expr')
@pg.production('expr : expr Span expr')
@pg.production('expr : expr Span')
@pg.production('expr :      Span expr')
@pg.production('expr :      Span')
def Span(p):
    if len(p) == 5:
        return Expression('Span', p[0], p[2], p[4])
    elif len(p) == 4:
        if isinstance(p[0], BaseExpression):
            return Expression('Span', p[0], Symbol('All'), p[3])
        elif isinstance(p[1], BaseExpression):
            return Expression('Span', Integer(1), p[1], p[3])
    elif len(p) == 3:
        if isinstance(p[0], BaseExpression):
            return Expression('Span', p[0], p[2])
        else:
            return Expression('Span', Integer(1), Symbol('All'),
                                 p[2])
    elif len(p) == 2:
        if isinstance(p[0], BaseExpression):
            return Expression('Span', args[1], Symbol('All'))
        elif isinstance(p[1], BaseExpression):
            return Expression('Span', Integer(1), p[1])
    elif len(p) == 1:
            return Expression('Span', Integer(1), Symbol('All'))

@pg.production('expr : Not expr')
@pg.production('expr : Factorial2 expr')
@pg.production('expr : Factorial expr')
def Not(p):
    if p[0].getstr() == '!!':
        return Expression('Not', Expression('Not', p[1]))
    else:
        return Expression('Not', p[1])

@pg.production('expr : symbol RawColon pattern RawColon expr')
@pg.production('expr : symbol RawColon expr')
def Pattern(p):
    if len(p) == 5:
        return Expression(
            'Optional', Expression('Pattern', Symbol(p[0]), p[2]), p[4])
    elif len(p) == 3:
        if p[2].get_head_name() == 'System`Pattern':
            return Expression(
                'Optional',
                Expression('Pattern', Symbol(p[0]), p[2].leaves[0]),
                p[2].leaves[1])
        else:
            return Expression('Pattern', Symbol(p[0]), p[2])

@pg.production('expr : pattern RawColon expr')
def Optional(p):
    return Expression('Optional', p[0], p[2])

@pg.production('expr : expr Postfix expr')
def Postfix(p):
    return Expression(p[2], p[0])

@pg.production('expr : expr TagSet expr Set expr')
@pg.production('expr : expr Set expr')
def Set(p):
    if len(p) == 3:
        return Expression('Set', p[0], p[2])
    elif len(p) == 5:
        return Expression('TagSet', p[0], p[2], p[4])

@pg.production('expr : expr TagSet expr SetDelayed expr')
@pg.production('expr : expr SetDelayed expr')
def SetDelayed(p):
    if len(p) == 3:
        return Expression('SetDelayed', p[0], p[2])
    elif len(p) == 5:
        return Expression('TagSetDelayed', p[0], p[2], p[4])

@pg.production('expr : expr TagSet expr Unset')
@pg.production('expr : expr Unset')
def p_Unset(p):
    if len(p) == 2:
        return Expression('Unset', args[1])
    elif len(p) == 4:
        return Expression('TagUnset', args[1], args[3])

@pg.production('expr : expr Function expr')
def Function(p):
    return Expression('Function', Expression('List', p[0]), p[2])

##def p_Put(self, args):
##    'expr : expr Put filename'
##    args[0] = Expression('Put', args[1], args[3])
##
##def p_PutAppend(self, args):
##    'expr : expr PutAppend filename'
##    args[0] = Expression('PutAppend', args[1], args[3])

@pg.production('expr : expr Semicolon expr')
@pg.production('expr : expr Semicolon')
def p_Compound(self, args):
    if p[0].get_head_name() == 'System`CompoundExpression':
        pass
    else:
        p[0] = Expression('CompoundExpression', p[0])
    if len(p) == 3:
        p[0].leaves.append(p[2])
    else:
        p[0].leaves.append(Symbol('Null'))
    return p[0]

##def p_box_to_expr(self, args):
##    '''expr : LeftBoxParenthesis boxes RightBoxParenthesis
##            | InterpretedBox LeftBoxParenthesis boxes RightBoxParenthesis %prec InterpretedBox'''   # nopep8
##    if len(args) == 4:
##        args[0] = args[2]
##    else:
##        result = Expression('MakeExpression', args[3])
##        args[0] = Expression('ReleaseHold', result)  # remove HoldComplete
##
##def p_box(self, args):
##    'box : expr'
##    args[0] = Expression('MakeBoxes', args[1])
##
##def p_form(self, args):
##    'form : expr'
##    if args[1].get_head_name() == 'System`Symbol':
##        args[0] = args[1]
##    else:
##        args[0] = Expression('Removed', String("$$Failure"))
##
##def p_boxes(self, args):
##    '''boxTOKEN : box
##                | boxTOKEN box
##          boxes : boxTOKEN
##                |'''
##    if len(args) == 1:
##        args[0] = String("")
##    if len(args) == 2:
##        if isinstance(args[1], list):
##            if len(args[1]) > 1:
##                args[0] = Expression('RowBox', *args[1])
##            else:
##                args[0] = args[1][0]
##        else:
##            args[0] = [args[1]]
##    elif len(args) == 3:
##        args[1].append(args[2])
##        args[0] = args[1]
##
##def p_RowBox(self, args):       # used for grouping raw boxes
##    'box : LeftBoxParenthesisInternal boxes RightBoxParenthesisInternal'
##    args[2].parenthesized = True
##    args[0] = args[2]
##
##def p_SuperscriptBox(self, args):
##    '''box : box Superscript box Otherscript box %prec Superscript
##           | box Superscript box'''
##    if len(args) == 4:
##        args[0] = Expression('SuperscriptBox', args[1], args[3])
##    elif len(args) == 6:
##        args[0] = Expression(
##            'SubsuperscriptBox', args[1], args[5], args[3])
##
##def p_Subscript(self, args):
##    '''box : box Subscript box Otherscript box %prec Subscript
##           | box Subscript box'''
##    if len(args) == 4:
##        args[0] = Expression('SubscriptBox', args[1], args[3])
##    elif len(args) == 6:
##        args[0] = Expression(
##            'SubsuperscriptBox', args[1], args[3], args[5])
##
##def p_OverscriptBox(self, args):
##    '''box : box Overscript box Otherscript box %prec Overscript
##           | box Overscript box'''
##    if len(args) == 4:
##        args[0] = Expression('OverscriptBox', args[1], args[3])
##    elif len(args) == 6:
##        args[0] = Expression(
##            'UnderoverscriptBox', args[1], args[5], args[3])
##
##def p_UnderscriptBox(self, args):
##    '''box : box Underscript box Otherscript box %prec Underscript
##           | box Underscript box'''
##    if len(args) == 4:
##        args[0] = Expression('UnderscriptBox', args[1], args[3])
##    elif len(args) == 6:
##        args[0] = Expression(
##            'UnderoverscriptBox', args[1], args[3], args[5])
##
##def p_FractionBox(self, args):
##    'box : box Fraction box'
##    args[0] = Expression('FractionBox', args[1], args[3])
##
##def p_SqrtBox(self, args):
##    '''box : Sqrt box Otherscript box %prec Sqrt
##           | Sqrt box'''
##    if len(args) == 3:
##        args[0] = Expression('SqrtBox', args[2])
##    elif len(args) == 5:
##        args[0] = Expression('RadicalBox', args[2], args[4])
##
##def p_FormBox(self, args):
##    'box : form FormBox box'
##    args[0] = Expression('FormBox', args[3], args[1])

# Construct lexer
lg = LexerGenerator()
for token, regex in tokens:
    lg.add(token, regex)
lg.ignore(r'\s+|(?s)\(\*.*?\*\)')
lexer = lg.build()

# Construct parser
parser = pg.build()
def parse(string):
    return parser.parse(lexer.lex(prelex(string)))
