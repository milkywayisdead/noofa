from . import query


_JOINS = {
    'inner': query.Join,
    'left': query.LeftJoin,
    'right': query.RightJoin,
}

_FILTERS = {
    '==': query.EqFilter,
    '!=': query.NeqFilter,
    '>': query.GtFilter,
    '>=': query.GeFilter,
    '<': query.LtFilter,
    '<=': query.LeFilter,
    'contains': query.ContainsFilter,
    'startswith': query.StartsWithFilter,
    'endswith': query.EndsWithFilter,
    'in': query.InFilter,
    'not in': query.NotInFilter,
}


def collect_tables(query_as_json):
    subqueries = _find_subqueries(query_as_json)
    tables = _find_tables([query_as_json] + subqueries)
    return list(set(tables))

def _find_subqueries(query):
    """
    Поиск подзапросов в запросе в виде словаря.
    """
    res = []

    try:
        query_filters = query.get('filters', [])
    except AttributeError:
        query_filters = query
    for filter_ in query_filters:
        is_q = filter_['is_complex']
        if is_q:
            res += _find_subqueries(filter_)
        else:
            val = filter_['value']
            try:
                is_subquery = val['is_subquery']
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
    return tables


class Qbuilder:
    """
    Конструктор запросов.
    """

    # В конструктов передаются:
    # словарь используемых в запросе таблиц вида {название таблицы: объект Table}
    # и запрос в виде словаря
    def __init__(self, tables, query, param_placeholder='%s', mssql=False):
        self._source = None  # источник данных
        self._base = query['base']
        self._tables = tables  # словарь таблиц
        self._base_table = self._tables[self._base]  # базовая таблица
        self._joins_list = query.get('joins', [])  # список соединений в запросе
        self._filters_list = query.get('filters', [])  # список фильтров в запросе
        self._values_list = query.get('values', [])  # список запрашиваемых полей
        self._limit = query.get('limit', None)  #  limit в запросе
        self._orderings = query.get('order_by', [])  # упорядочивание
        self._is_mssql = mssql

        try:
            int(self._limit)
        except:
            self._limit = None
        self._param_placeholder = param_placeholder

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
            l.has_field(on_l), r.has_field(on_r)
            joins.append(J(l, r, (on_l, on_r)))

        return joins

    def _parse_filters(self, f):
        """
        Построение объекта составного фильтра Q.
        """
        if f['is_complex'] == False:
            # если фильтр простой 
            # создать простой фильтр
            _filter = _FILTERS.get(f['op'], None)
            if _filter:
                val = f['value']
                # парсить подзапрос, если он является значением фильтра
                try:
                    is_subquery = val['is_subquery']
                except:
                    pass
                else:
                    if is_subquery:
                        qb = Qbuilder(self._tables, val)
                        val = qb.parse_query()

                table_name = f['table']
                field_name = f['field']
                table = self._tables[table_name]
                table.has_field(field_name)
                if table.enquote:
                    field_name = f'"{table_name}"."{field_name}"'
                else:
                    field_name = f'{table_name}.{field_name}'
                _filter = _filter(field_name, val, param_placeholder=self._param_placeholder)
                return query.Q(_filter)
        else:
            op = f['op'].lower()
            res = []
            for i in f['filters']:
                res.append(self._parse_filters(i))

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
        values, orderings = self._parse_values(), self._parse_orderings()
        q = self._base_table.select().join(*joins).where(*filters).values(*values)
        q = q.order_by(*orderings)

        if self._limit is not None:
            l = self._limit
            q.limit(l) if not self._is_mssql else q.mssql_limit(l)
        return q

    def _parse_values(self):
        result = []
        values_list = self._values_list
        for v in values_list:
            table = self._tables[v['table']]
            field_name = v['field']
            try:
                alias = v['alias']
            except KeyError:
                alias = None
            table.has_field(field_name)
            if table.enquote:
                value = f'"{table._name}"."{field_name}"'
            else:
                value = f'{table._name}.{field_name}'
            result.append((value, alias))
        return result

    def _parse_orderings(self):
        result = []
        for ordering in self._orderings:
            table = self._tables[ordering['table']]
            type_ = ordering['type'].upper()
            fields = ordering['fields']
            values = []
            for field_name in fields:
                table.has_field(field_name)
                if table.enquote:
                    value = f'"{table._name}"."{field_name}"'
                else:
                    value = f'{table._name}.{field_name}'
                if type_ != 'DESC':
                    type_ = 'ASC'
                values.append(value)
            result.append((values, type_))
        return result


def collect_query_filters():
    return list(_FILTERS.keys())
