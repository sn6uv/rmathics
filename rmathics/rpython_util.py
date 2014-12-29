try:
    import rpython
except ImportError:
    rpython = None


if rpython:
    def zip(list1, list2):
        """
        RPython does not support zip (expects two lists of equal length)
        """
        assert len(list1) == len(list2)
        for i in xrange(len(list1)):
            yield list1[i], list2[i]
        raise StopIteration

    def all(ls):
        """
        RPython does not suport all (expects list of Bool)
        """
        result = True
        for l in ls:
            if l is not True:
                result = False
        return result
else:
    all = all
    zip = zip

def replace(string, match, replace):
    """
    RPython only supports character replacement
    """
    if rpython:
        n = len(match)
        m = len(replace)
        i = 0
        while i <= len(string) - n:
            if string[i:i+n] == match:
                string = string[:i] + replace + string[i+n:]
                i += m-n+1
                assert i >= 0
            else:
                i += 1
        return string
    else:
        return string.replace(match, replace)


