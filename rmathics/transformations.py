from rmathics.definitions import BaseExpression, Expression, Symbol


def flatten(expr, depth=-1, head=None):
    """
    flattens an Expression
      - a negative depth allows for infinite recursion
      - only flattens subexpressions with given head
    """
    assert isinstance(expr, Expression)
    if depth == 0:
        return expr

    if head is None:
        head = expr.head
    assert isinstance(head, BaseExpression)     # head could be Expression

    leaves = []
    for leaf in expr.leaves:
        if leaf.head.eq(head):
            assert isinstance(leaf, Expression)
            for leaf2 in leaf.leaves:
                if isinstance(leaf2, Expression):
                    leaves.append(flatten(leaf2, head=head, depth=depth-1))
                else:
                    leaves.append(leaf2)
        else:
            if isinstance(leaf, Expression):
                leaves.append(flatten(leaf, head=head, depth=depth-1))
            else:
                leaves.append(leaf)
    expr = Expression(head)
    expr.leaves = leaves
    return expr


def thread(expr, head=Symbol('System`List')):
    """
    threads an Expression
      - given expr=f[args], thread over args whose head matches head
      - args whose heads don't match are repeated
    """
    assert isinstance(expr, Expression)
    assert isinstance(head, BaseExpression)

    messages = []
    args = expr.leaves
    exprhead = expr.head

    # indices of args with matching heads
    match_indices = [i for i, arg in enumerate(args) if arg.head.eq(head)]

    if match_indices == []:     # nothing to thread over
        return expr, messages

    # check all matching args have the same length
    thread_len = len(args[match_indices[0]].leaves)
    for i in match_indices:
        if args[i].leaves != thread_len:
            messages.append(('Thread', 'tdlen'))

    # args with heads that don't match are repeated thread_len times
    for i, arg in enumerate(args):
        if i in match_indices:
            args[i] = arg.leaves
        else:
            args[i] = thread_len * [arg]

    assert all([len(arg) == thread_len for arg in args])

    # thread over args
    leaves = []
    for i in xrange(thread_len):
        expr = Expression(exprhead)
        expr.leaves = [arg[i] for arg in args]
        leaves.append(expr)
    result = Expression(head)
    result.leaves = leaves
    return result, messages


def sort(expr):
    return expr
