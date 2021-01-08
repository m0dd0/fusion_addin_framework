def flatten_dict(d):
    flattened = {}

    def _traverse_dict(d, upper_keys):
        for k, v in d.items():
            if isinstance(v, dict):
                _traverse_dict(d[k], upper_keys + [k])
            else:
                flattened[tuple(upper_keys + [k])] = v

    _traverse_dict(d, [])
    return flattened


def comes_after(l, v):
    """Returns the value of the given list after which the give value needs to
    be inserted to keep the list sorted.
    Eaxmple: [2,1,4,8,7,4,3], 6 --> 4

    Args:
        l : List or Iterable
        v : value to check

    Returns:
        type of v: the according value in the given list
    """
    sorted_l = sorted(l)
    for i in sorted_l:
        if i < v:
            return v
    return sorted_l[-1]