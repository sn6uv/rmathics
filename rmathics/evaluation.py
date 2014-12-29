from rmathics.expression import Expression, Atom, Symbol
from rmathics.definitions import Definitions
from rmathics.transformations import flatten, thread, sort


def evaluate(expr, definitions=Definitions()):
    messages = []
    result = expr
    if isinstance(expr, Expression):
            # Evaluate head
            head, head_messages = evaluate(expr.head, definitions)
            messages.extend(head_messages)

            # Evaluate leaves
            leaves = []
            for leaf in expr.leaves:
                leaf, leaf_messages = evaluate(leaf, definitions)
                messages.extend(leaf_messages)
                leaves.append(leaf)

            # Build the result
            result = Expression(head)
            result.leaves = leaves

            # Apply transformations for Orderless, Listable, Flat
            if isinstance(head, Symbol):
                head_attributes = definitions.get_attributes(head.get_name())
                if 'Listable' in head_attributes:
                    result, thread_messages = thread(result)
                    messages.extend(thread_messages)
                if 'Orderless' in head_attributes:
                    result = sort(result)
                if 'Flat' in head_attributes:
                    result = flatten(result)

    elif isinstance(expr, Atom):
        if isinstance(expr, Symbol):
            # Apply user definitions
            # TODO OwnValues
            # TODO UpValues
            # TODO DownValues

            # Apply builtin definitions
            # TODO
            pass
        result = expr

    if expr.eq(result):
        return (result, messages)
    else:
        result, result_messages = evaluate(result, definitions)
        messages.extend(result_messages)
        return (result, messages)
