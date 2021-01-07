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