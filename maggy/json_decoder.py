import json

encoding = 'utf-8'


def convert_if_unicode(value):
    if isinstance(value, unicode):
        return value.encode(encoding)
    else:
        return value


def fix_encoding(items):
    result = {}
    for key, value in items:
        if key.isdigit():
            key = int(key)
        result[convert_if_unicode(key)] = convert_if_unicode(value)
    return result


class StringJSONDecoder(json.JSONDecoder):
    def __init__(self, **kwargs):
        kwargs['object_pairs_hook'] = fix_encoding
        json.JSONDecoder.__init__(self, **kwargs)
