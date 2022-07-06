from . import query
from .tests import pg


_JOINS = {
    'inner': query.Join,
    'left': query.LeftJoin,
    'right': query.RightJoin,
}

_FILTERS = {
    '==': query.EqFilter,
    '<>': query.NeqFilter,
    '>': query.GtFilter,
    '>=': query.GeFilter,
    '<': query.LtFilter,
    '<=': query.LeFilter,
    '%': query.LikeFilter,
    'in': query.InFilter,
}


def _find_subqueries(query_filters):
    """
    Поиск подзапросов в запросе в виде словаря.
    """
    res = []

    for f in query_filters:
        val = f['value']
        try:
            is_subquery = val['isSubquery']
        except:
            continue
        else:
            if is_subquery:
                res.append(val)
            filters = val.get('filters', [])
            res += _find_subqueries(filters)

    return res

def _find_tables(queries):
    """
    Получение списка таблиц по списку запросов в виде словаря.
    """
    tables = []
    for s in queries:
        _tables = s.get('tables', [])
        if _tables:
            tables += _tables

    return set(tables)


class Qbuilder:
    """
    Конструктор запросов.
    """

    # В конструктов передаются:
    # словарь используемых в запросе таблиц вида {название таблицы: объект Table}
    # и запрос в виде словаря
    def __init__(self, tables, query):
        self._source = None  # источник данных
        self._base = query['base']
        self._tables = tables  # словарь таблиц
        self._base_table = self._tables[self._base]  # базовая таблица
        self._joins_list = query.get('joins', [])  # список соединений в запросе
        self._filters_list = query.get('filters', [])  # список фильтров в запросе
        self._values_list = query.get('values', [])  # список запрашиваемых полей

    def parse_joins(self):
        """
        Построение соединений таблиц.
        Возвращается список объектов Join либо производных от Join классов.
        """
        joins = []

        for join in self._joins_list:
            l, r, j = join['l'], join['r'], join['j']
            on_l, on_r = join['on']['l'], join['on']['r']
            J = _JOINS.get(j, 'inner')
            l, r = self._tables[l], self._tables[r]

            joins.append(J(l, r, (on_l, on_r)))

        return joins
    
    def _parse_filters(self, f):
        """
        Построение объекта составного фильтра Q.
        """
        if f['isQ'] == False:
            # если фильтр простой 
            # создать простой фильтр
            _filter = _FILTERS.get(f['op'], None)
            if _filter:
                val = f['value']
                # парсить подзапрос
                try:
                    is_subquery = val['isSubquery']
                except:
                    pass
                else:
                    if is_subquery:
                        qb = Qbuilder(self._tables, val)
                        val = qb.parse_query()

                _filter = _filter(f['field'], val)
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

    def parse_filters(self):
        """
        Построение фильтров.
        Возвращается список составных фильтров Q. 
        """
        res = []

        for f in self._filters_list:
            res.append(self._parse_filters(f))

        return res

    def parse_query(self):
        """
        Построение запроса.
        Возвращается объект запроса SelectQuery.
        """
        joins, filters = self.parse_joins(), self.parse_filters()
        q = self._base_table.select().join(*joins).where(*filters)
        return q


# пример запроса
jsq = {
    'base': 'category',
    'tables': ['category', 'film_category'],
    'joins': [
        {'l': 'category', 'r': 'film_category', 'j': 'inner', 'on': {'l': 'category_id', 'r': 'category_id'}},
    ],
    'filters': [
        {'isQ': False, 'field': 'category.category_id', 'op': '==', 'value': 5},
        {'isQ': True, 'op': 'OR', 'filters': [
            {'isQ': False, 'field': 'category.category_id', 'op': '>', 'value': 5},
            {'isQ': False, 'field': 'category.category_id', 'op': '<', 'value': 100},
            {'isQ': True, 'op': 'AND', 'filters': [
                {'isQ': False, 'field': 'film_category.category_id', 'op': '>', 'value': 8},
                {'isQ': False, 'field': 'category.category_id', 'op': '<', 'value': 10},
            ]}
        ]},
    ],
    'values': [],
}

# пример запроса с подзапросами в фильтрах IN
jsq1 = {
    'base': 'category',
    'tables': ['category', 'film_category'],
    'joins': [
        {'l': 'category', 'r': 'film_category', 'j': 'inner', 'on': {'l': 'category_id', 'r': 'category_id'}},
    ],
    'filters': [
        {'isQ': False, 'field': 'category.category_id', 'op': 'in', 'value': {
            'isSubquery': True,
             'base': 'category',
             'tables': ['category'],
        }},
        {'isQ': False, 'field': 'category.category_id', 'op': 'in', 'value': {
            'isSubquery': True,
            'base': 'category',
            'tables': ['category'],
            'filters': [
                {'isQ': False, 'field': 'category.category_id', 'op': 'in', 'value': {
                    'isSubquery': True,
                    'base': 'category',
                    'tables': ['category'],
                }},
            ]
        }},
    ],
    'values': [],
}

def test():
    subs = _find_subqueries(jsq1['filters'])
    tables = jsq1['tables'] + list(_find_tables(subs))
    pg.open()
    tables = {t: pg.get_table(t) for t in tables}

    qb = Qbuilder(tables, jsq1)

    return qb