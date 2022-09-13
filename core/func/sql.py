from .base import SqlFunc, MandatoryArg, NonMandatoryArg


class SqlSelect(SqlFunc):
    """
    Функция построения select-запроса.
    """
    description = 'Функция построения select-запроса'
    args_description = [
        MandatoryArg('Базовая таблица', 0),
        NonMandatoryArg('Список соединений', 1),
        NonMandatoryArg('Список фильтров', 2),
        NonMandatoryArg('Список сортировок', 3),
        NonMandatoryArg('Список выбираемых полей', 4),
        NonMandatoryArg('Количество строк', 5),
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
        }
        try:
            for j in args[1]:
                j = j.q_part
                tables = [j['l'], j['r']]
                for table in tables:
                    if not table in jsq['tables']:
                        jsq['tables'].append(table)
                jsq['joins'].append(j)
        except IndexError:
            pass
        try:
            jsq['filters'] = [f.q_part for f in args[2]]
        except IndexError:
            pass
        try:
            jsq['order_by'] = [o.q_part for o in args[3]]
        except IndexError:
            pass
        try:
            for v in args[4]:
                tf = v.split('.')
                jsq['values'].append({'table': tf[0], 'field': tf[1]})
        except IndexError:
            pass
        try:
            n = args[5]
        except IndexError:
            pass
        else:
            jsq['limit'] = n
        print(jsq)
        return SqlDict(jsq)


class SqlJoin(SqlFunc):
    """
    Функция создания соединения таблиц в запросе.
    """
    description = 'Функция создания соединения таблиц в запросе'
    args_description = [
        MandatoryArg('Таблица1', 0),
        MandatoryArg('Таблица2', 1),
        MandatoryArg('Поле первой таблицы', 2),
        MandatoryArg('Поле второй таблицы', 3),
        NonMandatoryArg('Тип соединения', 4),
    ]

    @classmethod
    def get_name(self):
        return 'sql_join'

    def _operation(self, *args):
        try:
            type_ = args[4]
        except IndexError:
            type_ = 'inner'
        return SqlDict({
            'l': args[0], 
            'r': args[1], 
            'j': type_, 'on': {'l': args[2], 'r': args[3]},
        })


class SqlWhere(SqlFunc):
    """
    Функция создания фильтров where запросе.
    """
    description = 'Функция создания фильтров where запросе'
    args_description = [
        MandatoryArg('Название таблицы', 0),
        MandatoryArg('Название поля', 1),
        MandatoryArg('Тип фильтра', 2),
        MandatoryArg('Значение', 3),
    ]

    @classmethod
    def get_name(self):
        return 'sql_where'

    def _operation(self, *args):
        table_name, field_name = args[0], args[1]
        op, value = args[2], args[3]
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
    pass


class SqlDict:
    def __init__(self, dict_):
        self._q = dict_

    @property
    def q_part(self):
        return self._q


class SqlWhereDict(SqlDict):
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