import json


class StringJSONDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self)

    def default(self, o):
        obj = json.JSONDecoder.decode(self, o)
        if isinstance(obj, unicode):
            return obj.decode()
        else:
            return obj
