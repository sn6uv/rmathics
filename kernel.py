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


class Connection(object):
    def __init__(self, contents):
        contents = contents.strip()
        if not (contents[0] == '{' and contents[-1] == '}'):
            raise ValueError("Invalid enclosing {}")
        for entry in self.lrstrip1(contents).split(','):
            field, value = entry.split(':')
            field = field.strip()
            value = value.strip()
            if not (field[0] == field[-1] == '"'):
                raise ValueError("Invalid field %s" % field)
            field = self.lrstrip1(field)
            if value[0] == value[-1] == '"':
                value = self.lrstrip1(value)
                if field == 'transport':
                    self.transport = value
                elif field == 'signature_scheme':
                    self.signature_scheme = value
                elif field == 'ip':
                    self.ip = value
                elif field == 'key':
                    self.key = value
                else:
                    raise ValueError("Unknown str field %s" % field)
            elif value.isdigit():
                value = int(value)
                if field == 'control_port':
                    self.control_port = value
                elif field == 'shell_port':
                    self.shell_port = value
                elif field == 'stdin_port':
                    self.stdin_port = value
                elif field == 'hb_port':
                    self.hb_port = value
                elif field == 'iopub_port':
                    self.iopub_port = value
                else:
                    raise ValueError("Unknown int field %s" % field)
            else:
                raise ValueError("Unknown value type %s" % value)

    @staticmethod
    def lrstrip1(s):
        '''
        returns s[1:-1]
        '''
        istart = 1
        istop = len(s) - 1
        assert istop >= 1
        return s[istart:istop]

    def debug(self):
        print(self.control_port, self.shell_port, self.transport,
              self.signature_scheme, self.stdin_port, self.hb_port, self.ip,
              self.iopub_port, self.key)


def entry_point(argv):
    if len(argv) != 2:
        return 1
    try:
        connection = Connection(read_contents(argv[1]))
    except ValueError:
        return 1
    connection.debug()
    return 0


def target(*args):
    return entry_point, None


if __name__ == "__main__":
    entry_point(sys.argv)
