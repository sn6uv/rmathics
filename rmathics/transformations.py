from rmathics.expression import BaseExpression, Expression, Symbol
from rmathics.rpython_util import all


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
        if leaf.head.same(head):
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
    match_indices = [i for i, arg in enumerate(args) if arg.head.same(head)]

    if match_indices == []:     # nothing to thread over
        return expr, messages
    else:
        thread_len = len(args[match_indices[0]].leaves)

    # check all matching args have the same length
    for i in match_indices:
        if len(args[i].leaves) != thread_len:
            messages.append(('Thread', 'tdlen'))
            return expr, messages

    # args with heads that don't match are repeated thread_len times
    new_args = []
    for i, arg in enumerate(args):
        if i in match_indices:
            new_args.append(arg.leaves)
        else:
            new_args.append(thread_len * [arg])

    assert all([len(arg) == thread_len for arg in new_args])

    # thread over args
    leaves = []
    for i in xrange(thread_len):
        expr = Expression(exprhead)
        expr.leaves = [arg[i] for arg in new_args]
        leaves.append(expr)
    result = Expression(head)
    result.leaves = leaves
    return result, messages


def sort(expr):
    return expr
