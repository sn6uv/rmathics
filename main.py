import os
import sys

from rmathics.parser import parse, WaitInputError
from rmathics.evaluation import evaluate
from rmathics.definitions import Definitions


def run(fp):
    program_contents = ""
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        program_contents += read
    os.close(fp)

    definitions = Definitions()
    lines = iter(program_contents.split('\n'))
    for line in lines:
        new_messages = []
        while True:
            try:
                expr, messages = parse(line, definitions)
                break
            except WaitInputError:
                pass
            try:
                line = line + next(lines)
            except StopIteration:
                expr, messages = None, [('Syntax', 'sntup')]
                break
        for message in messages:
            print(message)
        if expr is None:
            continue
        result, messages = evaluate(expr, definitions)
        for message in messages:
            print(message)
        print(">>> " + line)
        print(result.repr())

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print("You must supply a filename")
        return 1
    run(os.open(filename, os.O_RDONLY, 0o777))
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
