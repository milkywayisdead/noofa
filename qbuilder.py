from . import query


class Qbuilder:
    """
    Строитель запросов.
    """
    
    def from_json(self):
        pass


_FILTERS = {
    '==': query.EqFilter,
    '<>': query.NeqFilter,
    '>': query.GtFilter,
    '>=': query.GeFilter,
    '<': query.LtFilter,
    '<=': query.LeFilter,
    '%': query.LikeFilter,
}


def parse(f):
    if f['isQ'] == False:
        # если фильтр простой 
        # создать простой фильтр
        _filter = _FILTERS.get(f['op'], None)
        if _filter:
            _filter = _filter(f['field'], f['value'])
            return query.Q(_filter)
    else:
        op = f['op'].lower()
        res = []
        for i in f['filters']:
            res.append(parse(i))
        q = query.Q()
        for i in res:
            if op == 'or':
                q |= query.Q(i)
            else:
                q &= query.Q(i)

        return q




jsq = {
    'base': 'users',
    'joins': [],
    'filters': {
        'Q1': {'isQ': False, 'field': 'id', 'op': '==', 'value': 5},
        'Q2': {'isQ': True, 'op': 'OR', 'filters': [
            {'isQ': False, 'field': 'id', 'op': '>', 'value': 5},
            {'isQ': False, 'field': 'id', 'op': '<', 'value': 100},
            {'isQ': True, 'op': 'AND', 'filters': [
                {'isQ': False, 'field': 'id', 'op': '>', 'value': 8},
                {'isQ': False, 'field': 'id', 'op': '<', 'value': 10},
            ]}
        ]},
    },
}

def f():
    q = []
    for f in jsq['filters'].values():
        q.append(parse(f))
    return q[0] & q[1]