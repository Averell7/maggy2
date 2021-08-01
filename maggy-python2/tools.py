

def nested_dict_search(obj, search, path=None, exact=False):
    """Search through a dictionary for a value either containing `search` (if exact=False) or equaling search (if
     exact = True).

     Returns a list of (path, value) tuples where path is a list of keys to the value and value is the value that was
     matched.

     Example:
     >>> test = {
     ...   "foo": {
     ...       "bar": ["baz"],
     ...   },
     ...   "baz": "abc",
     ...   "test": "baz",
     ...   "nested": {
     ...      "deep": {
     ...         "value": "the name is baz",
     ...      },
     ...   },
     ...}
    >>> nested_dict_search(test, "baz")
    [
        (['foo', 'bar', 0], 'baz'),
        (['test'], 'baz'),
        (['nested', 'deep', 'value'], 'the name is baz')
    ]

    """

    results = []

    if not path:
        path = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            _p = list(path)
            _p.append(key)
            results.extend(nested_dict_search(value, search, _p))
    elif isinstance(obj, list):
        for n, value in enumerate(obj):
            _p = list(path)
            _p.append(n)
            results.extend(nested_dict_search(value, search, _p))
    elif isinstance(obj, str):
        # Either exact or within match with strings
        if (not exact and str(search) in obj) or (exact and search == object):
            return [(path, obj)]
    elif search == obj:
        return [(path, obj)]

    return results


