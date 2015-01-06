import sys

from rpython.rtyper.lltypesystem import rffi
from rpython.translator.tool.cbuild import ExternalCompilationInfo

def entry_point(argv):
    # from rpython.rtyper.lltypesystem import rffi
    # from rpython.rtyper.lltypesystem.lltype import Struct

    ExternalCompilationInfo(
    #     includes=['gmp.h'],
    #     libraries=['gmp'],
    # )
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
