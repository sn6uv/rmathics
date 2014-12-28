import os


def subsets(items, min, max, included=None, less_first=False):
    if max is None:
        max = len(items)
    lengths = range(min, max + 1)
    if not less_first:
        lengths = reversed(lengths)
    lengths = list(lengths)
    if lengths and lengths[0] == 0:
        lengths = lengths[1:] + [0]

    def decide(chosen, not_chosen, rest, count):
        if count < 0 or len(rest) < count:
            return
        if count == 0:
            yield chosen, not_chosen + rest
        elif len(rest) == count:
            if included is None or all(item in included for item in rest):
                yield chosen + rest, not_chosen
        elif rest:
            item = rest[0]
            if included is None or item in included:
                for set in decide(chosen + [item], not_chosen, rest[1:],
                                  count - 1):
                    yield set
            for set in decide(chosen, not_chosen + [item], rest[1:], count):
                yield set

    for length in lengths:
        for chosen, not_chosen in decide([], [], items, length):
            yield chosen, ([], not_chosen)


def subranges(items, min_count, max, flexible_start=False, included=None,
              less_first=False):
    # TODO: take into account included

    if max is None:
        max = len(items)
    max = min(max, len(items))
    if flexible_start:
        starts = range(len(items) - max + 1)
    else:
        starts = (0,)
    for start in starts:
        lengths = range(min_count, max + 1)
        if not less_first:
            lengths = reversed(lengths)
        lengths = list(lengths)
        if lengths == [0, 1]:
            lengths = [1, 0]
        for length in lengths:
            yield (items[start:start + length],
                   (items[:start], items[start + length:]))


def permutations(items, without_duplicates=True):
    if not items:
        yield []
    # already_taken = set()
    # first yield identical permutation without recursion
    yield items
    for index in range(len(items)):
        item = items[index]
        # if item not in already_taken:
        for sub in permutations(items[:index] + items[index + 1:]):
            yield [item] + sub
            # already_taken.add(item)


def get_file_time(file):
    try:
        return os.stat(file).st_mtime
    except OSError:
        return 0
