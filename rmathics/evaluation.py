from rmathics.expression import Expression, Atom, Symbol
from rmathics.definitions import Definitions


def evaluate(expr, definitions=Definitions()):
    messages = []
    result = expr
    if isinstance(expr, Expression):
            leaves = []
            for leaf in expr.leaves:
                leaf, leaf_messages = evaluate(leaf, definitions)
                messages.extend(leaf_messages)
            head, head_messages = evaluate(expr.head, definitions)
            messages.extend(head_messages)
            result = Expression(head)
            result.leaves = leaves
            result.evaluated = True
            result = expr
    elif isinstance(expr, Atom):
        if isinstance(expr, Symbol):
            # TODO OwnValues
            # TODO UpValues
            # TODO DownValues
            result = expr
        result = expr
    return (result, messages)
