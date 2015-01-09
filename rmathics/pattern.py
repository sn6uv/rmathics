from rmathics.expression import Atom, Symbol, Expression


def match(expr, pattern):
    """
    determine whether the expr matches the pattern
    if it doesn't match return (False, {})

    if the pattern matches return True and a list of named mappings from
    pattern names to sub expressions.
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
        doesmatch, mapping = match(expr, patt)
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
        return _match_seq(expr.leaves, pattern.leaves)
        raise NotImplementedError
    else:
        print phead.repr()
        return False, {}


def merge_dicts(dict1, dict2):
    """
    merge 2 dicts but raise ValueError if collisions do not agree
    """
    result = dict1
    for key in dict2:
        value = result.get(key, None)
        if value is not None:
            if not result.same(value, dict2[key]):
                raise ValueError
        result[key] = dict2[key]
    return result


def _match_seq(exprs, patts):
    """
    matches a list of expressions against a list of patterns

    We match by pairing each pattern to list of expressions
      - BlankSequence matches to one or more expression
      - BlankNullSequence matches to zero or more
      - everything else (including Blank[]) matches to exactly one expression

    Try to match the 'everything else' first (hence the name high_prec_xxx)
    because it's more efficient this way.
    """
    if len(patts) == len(exprs) == 0:
        return True, {}

    patti, name = None, None
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
    if patti is not None:       # everything else
        patt = patts[patti]
        for expri, expr in enumerate(exprs):
            if match(expr, patt):
                match0, mapping0 = _match_seq(
                    exprs[:expri], patts[:patti])
                match1, mapping1 = _match_seq(
                    exprs[expri+1:], patts[patti+1:])
                try:
                    mapping = merge_dicts(mapping0, mapping1)
                    if match0 and match1:
                        if name is not None:
                            mapping = merge_dicts(mapping, {name: expr})
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
    if patti is not None:       # BlankSequence
        for match_len in range(1, len(exprs)+1):
            # begin looking for length 1 matches
            for start_pos in range(len(exprs)+1-match_len):
                match0, mapping0 = _match_seq(
                    exprs[:start_pos], patts[:patti])
                match1, mapping1 = _match_seq(
                    exprs[start_pos+match_len:], patts[patti+1:])
                expr = Expression(Symbol('System`Sequence'),
                                  *exprs[start_pos:start_pos+match_len])
                try:
                    mapping = merge_dicts(mapping0, mapping1)
                    if match0 and match1:
                        if name is not None:
                            mapping = merge_dicts(mapping, {name: expr})
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
    else:
        assert patt.head.same(Symbol('System`BlankNullSequence'))
    for match_len in range(0, len(exprs)+1):
        # begin looking for length 0 matches
        for start_pos in range(len(exprs)+1-match_len):
            match0, mapping0 = _match_seq(
                exprs[:start_pos], patts[:patti])
            match1, mapping1 = _match_seq(
                exprs[start_pos+match_len:], patts[patti+1:])
            expr = Expression(Symbol('System`Sequence'),
                              *exprs[start_pos:start_pos+match_len])
            try:
                mapping = merge_dicts(mapping0, mapping1)
                if match0 and match1:
                    if name is not None:
                        mapping = merge_dicts(mapping, {name: expr})
                    return True, mapping
            except ValueError:
                pass
    return False, {}
