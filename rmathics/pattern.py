from rmathics.expression import Atom, Symbol, Expression
from rmathics.rpython_util import all, permutations


def match(expr, pattern, definitions):
    """
    determine whether the expr matches the pattern
    if it doesn't match return (False, {})

    if the pattern matches return True and a dict {str: BaseExpression} which
    maps pattern names to matches subexpressions.
    """

    if isinstance(pattern, Atom):
        return (expr.same(pattern), {})
    assert isinstance(pattern, Expression)
    phead = pattern.head
    if phead.same(Symbol('System`Pattern')):
        if len(pattern.leaves) != 2:
            # TODO message Pattern::argr:
            return False, {}
        name, patt = pattern.leaves
        name = name.get_name()
        doesmatch, mapping = match(expr, patt, definitions)
        if doesmatch:
            if name in mapping.keys():
                # a recursive name can never match e.g. x:_^x_
                return False, {}
            mapping[name] = expr
            return True, mapping
    elif (phead.same(Symbol('System`Blank')) or
          phead.same(Symbol('System`BlankSequence')) or
          phead.same(Symbol('System`BlankNullSequence'))):
        if len(pattern.leaves) == 0:
            return True, {}
        elif len(pattern.leaves) == 1:
            if expr.head.same(pattern.leaves[0]):
                return True, {}
            else:
                return False, {}
        else:
            # TODO message p.head::argt
            return False, {}
    elif phead.same(expr.head):
        head_attributes = definitions.get_attributes(phead.get_name())
        if 'Orderless' in head_attributes:
            for leaves in permutations(expr.leaves):
                match0, mapping = _match_seq(leaves, pattern.leaves, definitions)
                if match0:
                    return match0, mapping
            return False, {}
        return _match_seq(expr.leaves, pattern.leaves, definitions)
    return False, {}


def _merge_dicts(dict1, dict2):
    """
    merge 2 dicts but raise ValueError if collisions do not agree.

    dicts should be of the form {str: BaseExpression}

    TIP: since we loop over dict2, it's more efficient for dict2 to be smaller
    """
    result = dict1
    for key in dict2:
        value = result.get(key, None)
        if value is not None:
            if not value.same(dict2[key]):
                raise ValueError
        result[key] = dict2[key]
    return result


def _match_seq(exprs, patts, definitions):
    """
    matches a list of expressions against a list of patterns

    We match by pairing each pattern to a list of expressions
      - BlankSequence matches to one or more expression
      - BlankNullSequence matches to zero or more
      - everything else (including Blank[]) matches to exactly one expression

    Try to match the 'everything else' first. It's more efficient this way.

    returns (bool, {str: BaseExpression}) like the function match above.
    """
    if len(patts) == len(exprs) == 0:
        return True, {}

    patti, name = -1, None
    for i, patt in enumerate(patts):
        if patt.head.same(Symbol('System`Pattern')):
            if len(patt.leaves) != 2:
                # TODO message Pattern::argr:
                return False, {}
            name2, patt2 = patt.leaves
            if patt2.head.same(Symbol('System`BlankSequence')):
                continue
            if patt2.head.same(Symbol('System`BlankNullSequence')):
                continue
            else:
                name = name2.get_name()
                patti = i
                break
        if patt.head.same(Symbol('System`BlankSequence')):
            continue
        elif patt.head.same(Symbol('System`BlankNullSequence')):
            continue
        else:
            patti = i
            break
    if patti >= 0:       # everything else
        patt = patts[patti]
        if patt.head.same(Symbol('System`Pattern')):
            patt = patt.leaves[0]
        for expri, expr in enumerate(exprs):
            match0, mapping0 = match(expr, patt, definitions)
            if match0:
                match1, mapping1 = _match_seq(
                    exprs[:expri], patts[:patti], definitions)
                match2, mapping2 = _match_seq(
                    exprs[expri+1:], patts[patti+1:], definitions)
                try:
                    if match1 and match2:
                        mapping = _merge_dicts(mapping1, mapping2)
                        mapping = _merge_dicts(mapping, mapping0)
                        if name is not None:
                            mapping = _merge_dicts(mapping, {name: expr})
                        return True, mapping
                except ValueError:
                    pass
        return False, {}

    for i, patt in enumerate(patts):
        if patt.head.same(Symbol('System`Pattern')):
            assert len(patt.leaves) == 2
            name2, patt2 = patt.leaves
            if patt2.head.same(Symbol('System`BlankSequence')):
                name = name2.get_name()
                patti = i
                break
        if patt.head.same(Symbol('System`BlankSequence')):
            patti = i
            break
    if patti >= 0:
        patt = patts[patti]
        if patt.head.same(Symbol('System`Pattern')):
            patt = patt.leaves[1]
        for match_len in range(1, len(exprs)+1):
            # begin looking for length 1 matches
            for start_pos in range(len(exprs)+1-match_len):
                if len(patt.leaves) == 0:
                    pass
                elif len(patt.leaves) == 1:
                    if not all([expr.head.same(patt.leaves[0]) for expr in
                                exprs[start_pos:start_pos+match_len]]):
                        continue
                else:
                    raise ValueError
                match0, mapping0 = _match_seq(
                    exprs[:start_pos], patts[:patti], definitions)
                match1, mapping1 = _match_seq(
                    exprs[start_pos+match_len:], patts[patti+1:], definitions)
                expr = Expression(Symbol('System`Sequence'))
                expr.leaves = exprs[start_pos:start_pos+match_len]
                try:
                    mapping = _merge_dicts(mapping0, mapping1)
                    if match0 and match1:
                        if name is not None:
                            mapping = _merge_dicts(mapping, {name: expr})
                        return True, mapping
                except ValueError:
                    pass
        return False, {}

    if patts == []:
        assert exprs != []
        return False, {}
    patti = 0
    patt = patts[patti]
    if patt.head.same(Symbol('System`Pattern')):
            assert len(patt.leaves) == 2
            name2, patt2 = patt.leaves
            name = name2.get_name()
            assert patt2.head.same(Symbol('System`BlankNullSequence'))
            patt = patt2
    else:
        assert patt.head.same(Symbol('System`BlankNullSequence'))
    for match_len in range(0, len(exprs)+1):
        # begin looking for length 0 matches
        for start_pos in range(len(exprs)+1-match_len):
            if len(patt.leaves) == 0:
                pass
            elif len(patt.leaves) == 1:
                if not all([expr.head.same(patt.leaves[0]) for expr in
                            exprs[start_pos:start_pos+match_len]]):
                    continue
            else:
                raise ValueError
            match0, mapping0 = _match_seq(
                exprs[:start_pos], patts[:patti], definitions)
            match1, mapping1 = _match_seq(
                exprs[start_pos+match_len:], patts[patti+1:], definitions)
            expr = Expression(Symbol('System`Sequence'))
            expr.leaves = exprs[start_pos:start_pos+match_len]
            try:
                mapping = _merge_dicts(mapping0, mapping1)
                if match0 and match1:
                    if name is not None:
                        mapping = _merge_dicts(mapping, {name: expr})
                    return True, mapping
            except ValueError:
                pass
    return False, {}
