from .base import SqlFunc, MandatoryArg, NonMandatoryArg


class SqlQuery(SqlFunc):
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

    def _operation(self, *args):
        jsq = {
            'base': args[1],
            'joins': [],
            'filters': [],
            'values': [],
        }
        try:
            jsq['joins'] = args[1]
        except IndexError:
            pass
        try:
            jsq['filters'] = args[2]
        except IndexError:
            pass
        try:
            jsq['order_by'] = args[3]
        except IndexError:
            pass
        try:
            jsq['values'] = args[4]
        except IndexError:
            pass
        try:
            n = args[5]
        except IndexError:
            pass
        else:
            jsq['limit'] = n
        return jsq


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

    def _operation(self, *args):
        try:
            type_ = args[4]
        except IndexError:
            type_ = 'inner'
        return {
            'l': args[0], 
            'r': args[1], 
            'j': type_, 'on': {'l': args[2], 'r': args[3]}
        }


class SqlWhere(SqlFunc):
    pass


class SqlOrderBy(SqlFunc):
    pass