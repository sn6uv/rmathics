from rmathics.expression import Atom, Symbol, Expression


def match(expr, pattern, matches=False):
    """
    determine whether the expr matches the pattern
    if it doesn't match return (False, {})

    if `matches` is True also return a list of named mappings from pattern
    names to sub expressions. If `matches` false, the dict will be empty
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
        doesmatch, mappings = match(expr, patt, matches=matches)
        if doesmatch:
            if name in mappings.keys():
                # a recursive name can never match e.g. x:_^x_
                return False, {}
            mappings[name] = expr
            return True, mappings
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
        return _match_seq(expr.leaves, pattern.leaves, matches=matches)
        raise NotImplementedError
    else:
        print phead.repr()
        return False, {}


def _match_seq(exprs, patts, matches=False):
    """
    matches a list of expressions against a list of patterns
    """
    if len(exprs) == len(patts) == 1:
        return match(exprs[0], patts[0], matches=matches)
    high_prec_indices = []
    blank_seq_indices = []
    blank_nul_indices = []
    for patti, patt in enumerate(patts):
        if patt.head.same(Symbol('System`BlankSequence')):
            blank_seq_indices.append(patti)
        elif patt.head.same(Symbol('System`BlankNullSequence')):
            blank_nul_indices.append(patti)
        else:
            high_prec_indices.append(patti)

    if high_prec_indices:
        patti = high_prec_indices[0]
        patt = patts[patti]
        for expri, expr in enumerate(exprs):
            if match(expr, patt):
                match0, mapping0 = _match_seq(
                    exprs[:expri], patts[:patti])
                match1, mapping1 = _match_seq(
                    exprs[expri+1:], patts[patti+1:])
                if match0 and match1:
                    return True, {}
        return False, {}
    if blank_seq_indices:
        patti = blank_seq_indices[0]
        for match_len in range(1, len(exprs)):
            # begin looking for length 1 matches
            for start_pos in range(len(exprs)-match_len):
                match0, mapping0 = _match_seq(
                    exprs[:start_pos], patts[:patti])
                match1, mapping1 = _match_seq(
                    exprs[start_pos+match_len:], patts[patti+1:])
                if match0 and match:
                    return True, {}
        return False, {}
    if blank_nul_indices:
        patti = blank_nul_indices[0]
        if exprs == []:
            return True, {}
        for match_len in range(0, len(exprs)):
            # begin looking for length 0 matches
            for start_pos in range(len(exprs)-match_len):
                match0, mapping0 = _match_seq(
                    exprs[:start_pos], patts[:patti])
                match1, mapping1 = _match_seq(
                    exprs[start_pos+match_len:], patts[patti+1:])
                if match0 and match:
                    return True, {}
        return False, {}
    assert patts == []
    return True, {}
