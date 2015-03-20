# Level
NOTSET = 0
DEBUG = 10
INFO = 20
WARN = 30
WARNING = 30
ERROR = 40
FATAL = 50
CRITICAL = 50

# Defaults
BASIC_FORMAT = '%s:%s:%s'
_level = NOTSET
_name = 'root'


def _log(msg):
    print(msg)


def warn(msg):
    global _level, _name, BASIC_FORMAT, WARN
    if _level <= WARN:
        _log(BASIC_FORMAT % ('WARN', _name, msg))


def debug(msg):
    global _level, _name, BASIC_FORMAT, DEBUG
    if _level <= DEBUG:
        _log(BASIC_FORMAT % ('DEBUG', _name, msg))


def info(msg):
    global _level, _name, BASIC_FORMAT, INFO
    if _level <= INFO:
        _log(BASIC_FORMAT % ('INFO', _name, msg))


def fatal(msg):
    global _level, _name, BASIC_FORMAT, FATAL
    if _level <= FATAL:
        _log(BASIC_FORMAT % ('FATAL', _name, msg))


def basicConfig(level=INFO):
    global _level
    _level = level
