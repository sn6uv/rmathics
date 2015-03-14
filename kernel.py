import os
import sys


def read_contents(filename):
    fp = os.open(filename, os.O_RDONLY, 0o777)
    contents = ''
    while True:
        read = os.read(fp, 4096)
        if len(read) == 0:
            break
        contents += read
    os.close(fp)
    return contents


def lrstrip1(s):
    '''
    returns s[1:-1]
    '''
    istart = 1
    istop = len(s) - 1
    assert istop >= 1
    return s[istart:istop]


def parse_json(contents):
    '''
    simple json parser
    '''
    result = {}
    contents = contents.strip()
    if not (contents[0] == '{' and contents[-1] == '}'):
        print 1
        raise ValueError("Invalid enclosing {}")
    for entry in lrstrip1(contents).split(','):
        field, value = entry.split(':')
        field = field.strip()
        value = value.strip()
        if not (field[0] == field[-1] == '"'):
            print 2
            raise ValueError("Invalid field %s" % field)
        field = lrstrip1(field)
        if value[0] == value[-1] == '"':
            # value = lrstrip1(value)
            pass
        elif value.isdigit():
            # value = int(value)
            pass
        else:
            print 3
            raise ValueError("Invalid type %s" % value)
        result[field] = value
    return result


def entry_point(argv):
    if len(argv) != 2:
        return 1
    try:
        connection = parse_json(read_contents(argv[1]))
    except ValueError:
        return 1
    for key in connection:
        print(key, connection[key])
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
