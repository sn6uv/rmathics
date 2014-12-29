from rmathics.definitions import BaseExpression, Expression, Symbol

def flatten(expr, depth=-1, head=None):
    """
    flattens an Expression
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

def thread(expr):
    return expr

def sort(expr):
    return expr
