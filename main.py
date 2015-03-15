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
        print(">>> " + line)
        for message in messages:
            print(message)
        if expr is None:
            continue
        result, messages = evaluate(expr, definitions)
        for message in messages:
            print(message)
        print(result.repr())


def entry_point(argv):
    if len(argv) == 1:
        run(0)  # read from stdin
    else:
        for filename in argv[1:]:
            fp = os.open(filename, os.O_RDONLY, 0o777)
            run(fp)
            os.close(fp)
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
