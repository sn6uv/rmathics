"""
A reimplementation of some useful python utilities missing from RPython
"""

def zip(list1, list2):
    """
    expects two lists of equal length
    """
    assert len(list1) == len(list2)
    for i in xrange(len(list1)):
        yield list1[i], list2[i]
    raise StopIteration


def all(ls):
    """
    expects list of Bool
    """
    result = True
    for l in ls:
        if l is not True:
            result = False
    return result


def permutations(pool):
    """
    based on itertools.permutations
    """
    n = len(pool)
    indices = range(n)
    cycles = range(n, 0, -1)
    yield pool
    while n:
        for i in range(n-1, -1, -1):
            cycles[i] -= 1
            if cycles[i] == 0:
                num = indices[i]
                for k in range(i, n-1):
                    indices[k] = indices[k+1]
                indices[n-1] = num
                cycles[i] = n-i
            else:
                j = cycles[i]
                indices[i], indices[-j] = indices[-j], indices[i]
                yield [pool[i] for i in indices]
                break
        else:
            return


def replace(string, match, replace):
    """
    RPython only supports character replacement

    reimplements string.replace(match, replace)
    """
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
