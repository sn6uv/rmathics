import sys
from rpython.translator.tool.cbuild import ExternalCompilationInfo


def entry_point(argv):
    info = ExternalCompilationInfo()
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
