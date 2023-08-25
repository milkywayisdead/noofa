from datetime import datetime

from ..sources.utils import Qbuilder, collect_tables
from .base import SqlFunc, MandatoryArg, NonMandatoryArg


class SqlDict:
    """
    Обертка для select-запросов и их частей в виде словарей.
    Используется для упрощенного сложения запросов и фильтров
    в виде словарей.
    """
    def __init__(self, dict_):
        self._q = dict_

    @property
    def q_part(self):
        return self._q

    def keys(self):
        return self._q.keys()

    def values(self):
        return self._q.values()

    def __getitem__(self, key):
        return self._q[key]


class SqlWhereDict(SqlDict):
    """
    Обертка для фильтров where в виде словарей.
    """
    def __and__(self, value):
        return SqlWhereDict({
            'is_complex': True,
            'op': 'AND',
            'filters': [self.q_part, value.q_part],
        })

    def __or__(self, value):
        return SqlWhereDict({
            'is_complex': True,
            'op': 'OR',
            'filters': [self.q_part, value.q_part],
        })


class SqlExecute(SqlFunc):
    """
    Функция выполнения sql-запроса.
    """
    group = 'sql'
    description = 'Функция выполнения sql-запроса'
    args_description = [
        MandatoryArg('Объект соединения', 0),
        MandatoryArg('Объект запроса', 1),
    ]

    @classmethod
    def get_name(cls):
        return 'sql_execute'

    def _operation(self, *args):
        conn = args[0]
        q = args[1].q_part
        tables_list = collect_tables(q)
        conn.open()
        tables = conn.get_table_multiple(tables_list)
        qb = Qbuilder(tables, q)
        query = qb.parse_query()
        data = conn.get_data(query=query)
        conn.close()
        return data


class SqlSelect(SqlFunc):
    """
    Функция построения select-запроса.
    """
    description = 'Функция построения select-запроса'
    args_description = [
        MandatoryArg('Базовая таблица', 0, [str]),
        NonMandatoryArg('Список соединений', 1, [list, SqlDict]),
        NonMandatoryArg('Список фильтров', 2, [list, SqlWhereDict]),
        NonMandatoryArg('Список сортировок', 3, [list, SqlDict]),
        NonMandatoryArg('Список выбираемых полей', 4, [list]),
        NonMandatoryArg('Количество строк', 5, [int, str]),
    ]

    @classmethod
    def get_name(self):
        return 'sql_select'

    def _operation(self, *args):
        jsq = {
            'is_subquery': True,
            'tables': [args[0], ],
            'base': args[0],
            'joins': [],
            'filters': [],
            'values': [],
            'order_by': [],
        }
        try:
            joins = args[1]
            if isinstance(joins, list):
                for j in joins:
                    j = j.q_part
                    tables = [j['l'], j['r']]
                    for table in tables:
                        jsq['tables'].append(table)
                    jsq['joins'].append(j)
            else:
                j = joins.q_part
                jsq['joins'].append(j)
                jsq['tables'] += [j['l'], j['r']]
        except IndexError:
            pass
        try:
            filters_ = args[2]
            if isinstance(filters_, list):
                jsq['filters'] = [f.q_part for f in args[2]]
            else:
                jsq['filters'].append(filters_.q_part)
        except IndexError:
            pass
        try:
            orderings = args[3]
            if isinstance(orderings, list):
                jsq['order_by'] = [o.q_part for o in orderings]
            else:
                jsq['order_by'].append(orderings.q_part)
        except IndexError:
            pass
        try:
            for v in args[4]:
                alias = None
                if isinstance(v, list):
                    tf, alias = v[0].split('.'), v[1]
                else:
                    tf = v.split('.')
                value = {'table': tf[0], 'field': tf[1]}
                if alias is not None:
                    value['alias'] = alias
                jsq['values'].append(value)
        except IndexError:
            pass
        try:
            n = args[5]
        except IndexError:
            pass
        else:
            jsq['limit'] = n
        jsq['tables'] = list(set(jsq['tables']))
        return SqlDict(jsq)


class SqlJoin(SqlFunc):
    """
    Функция создания соединения таблиц в запросе.
    """
    description = 'Функция создания соединения таблиц в запросе'
    args_description = [
        MandatoryArg('Первая таблица и поле', 0, [str]),
        MandatoryArg('Вторая таблица и поле', 1, [str]),
        NonMandatoryArg('Тип соединения', 2, [str]),
    ]

    @classmethod
    def get_name(self):
        return 'sql_join'

    def _operation(self, *args):
        try:
            type_ = args[2]
        except IndexError:
            type_ = 'inner'
        l, lf = args[0].split('.')
        r, rf = args[1].split('.')
        return SqlDict({
            'l': l,
            'r': r,
            'j': type_, 'on': {'l': lf, 'r': rf},
        })


class SqlWhere(SqlFunc):
    """
    Функция создания фильтров where в запросе.
    """
    description = 'Функция создания фильтров where в запросе'
    args_description = [
        MandatoryArg('Название таблицы и поля', 0, [str]),
        MandatoryArg('Тип фильтра', 1, [str]),
        MandatoryArg('Значение', 2, [str, int, float, list, SqlDict, datetime]),
    ]

    @classmethod
    def get_name(self):
        return 'sql_where'

    def _operation(self, *args):
        table_name, field_name = args[0].split('.')
        op, value = args[1], args[2]
        try:
            value = value.q_part
        except:
            pass
        return SqlWhereDict({
            'is_complex': False,
            'table': table_name,
            'field': field_name,
            'op': op,
            'value': value,
        })


class SqlOrderBy(SqlFunc):
    """
    Функция создания упорядочивания в запросе.
    """
    description = 'Функция создания упорядочивания в запросе'
    args_description = [
        MandatoryArg('Название таблицы и поля', 1, [str]),
        MandatoryArg('Направление', 0, [str]),
    ]

    @classmethod
    def get_name(self):
        return 'sql_orderby'

    def _operation(self, *args):
        table_name, field = args[1].split('.')
        ordering = args[0]
        return SqlDict({
            'table': table_name,
            'fields': [field],
            'type': ordering,
        })
