from datetime import date, time
from json import JSONEncoder


class NoofaJsonEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, time)):
            return obj.isoformat()
        return JSONEncoder.default(self, obj)
