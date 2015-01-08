import os
import sys

from rmathics.parser import parse
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
    for line in program_contents.split('\n'):
        expr, messages = parse(program_contents, definitions)
        for message in messages:
            print(message)
        result, messages = evaluate(expr, definitions)
        for message in messages:
            print(message)
        x = result.repr()

def entry_point(argv):
    try:
        filename = argv[1]
    except IndexError:
        print("You must supply a filename")
        return 1
    run(os.open(filename, os.O_RDONLY, 0777))
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
