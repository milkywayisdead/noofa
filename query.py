
class NoSuchFieldError(Exception):
    pass


# ДОБАВИТЬ ПРОВЕРКУ ОБЪЕДИНЕНИЙ, ФИЛЬТРОВ И ПОЛЕЙ НА УНИКАЛЬНОСТЬ?


class Join:
    """
    Объединение таблиц.
    """

    join_type = 'INNER'

    def __init__(self, table1, table2, on):
        self._left = table1  # первая таблица
        self._right = table2  # вторая таблица

        """ 
        Список или кортеж, элементы которого - названия полей
        таблиц, по которым делается объединение;
        первый элемент - для левой таблицы, второй - для правой.
        """
        self._on = on  

    def __str__(self):
        right_name, left_name = self._right._name, self._left._name
        s = f'{self.__class__.join_type} JOIN {right_name} '
        s += f'ON {left_name}.{self._on[0]} = {right_name}.{self._on[1]}'
        return s


class LeftJoin(Join):
    join_type = 'LEFT OUTER'


class RightJoin(Join):
    join_type = 'RIGHT OUTER'


class SelectQuery:
    """
    Select-запрос.
    """

    def __init__(self, table, *fields):
        self._fields = []  # список возможных полей в запросе
        self._where = []  # список фильтров в запросе
        self._joins = []  # список объединений в запросе
        self._params = []  # список параметров для фильтров запроса
        self._table = table  # таблица
        self._values = []

        for f in table.get_verbose_names():
            self._fields.append(f)

        self.values(*fields)

    def join(self, *joins):
        """
        Добавление объединения/объединений в запрос.
        """
        for j in joins:
            right, left = j._right, j._left
            if self._table == right or self._table == left:
                self._joins.append(j)

                if self._table == right:
                    t = left
                else:
                    t = right

                for f in t.get_verbose_names():
                    if not f in self._fields:
                        self._fields.append(f)

        return self

    def where(self, *filters):
        """
        Добавление фильтров в запрос.
        """
        for f in filters:
            self._where.append(f)
            for p in f._params:
                self._params.append(p)

        return self

    @property
    def params(self):
        """
        Список параметров в фильтрах запроса.
        """
        return self._params

    def values(self, *fields):
        for f in fields:
            if f in self._fields:
                if f not in self._values:
                    self._values.append(f)
            else:
                raise NoSuchFieldError(f'Поле {f} недоступно в запросе')

    def execute(self, cursor):
        q = str(self)
        params = self._params

        if params:
            cursor.execute(q, params)
        else:
            cursor.execute(q)

        return cursor.fetchall()

    def __str__(self):
        if self._values:
            fields = f', '.join(self._values)
        else:
            fields = f', '.join(self._fields)

        q = f'SELECT {fields} FROM {self._table._name}'

        _joins = ''
        if self._joins:          
            for j in self._joins:
                _joins += f'{str(j)} '

        if _joins != '':
            q += f' {_joins}'

        _where = ''
        if self._where:
            filters = [str(f) for f in self._where]
            _where = ' AND '.join(filters)

        if _where:
            q += f' WHERE {_where}'

        return q


class Q:
    """
    Составной фильтр.
    """
    def __init__(self, *filters):
        self._filters = []
        self._params = []
        self._q = []

        for f in filters:
            self._filters.append(f)
            for p in f._params:
                self._params.append(p)

    @property
    def params(self):
        """
        Список параметров в фильтрах запроса.
        """
        return self._params
    
    def __str__(self):
        filters = [str(f) for f in self._filters]
        s = f"({' AND '.join(filters)})"

        if self._q:
            for f in self._q:
                s += f" {f[1]} {str(f[0])}"

        return s

    def __and__(self, value):
        if type(value) is Q:
            self._q.append((value, 'AND'))
            self._params += value._params
            return self
        raise TypeError(f'Недопустимый операнд: {value}')

    def __or__(self, value):
        if type(value) is Q:
            self._q.append((value, 'OR'))
            self._params += value._params
            return self
        raise TypeError(f'Недопустимый операнд: {value}')


class Filter:
    """
    Фильтр (WHERE в запросе).
    """

    def __init__(self, field_name, value):
        self._field_name = field_name
        self._params = [value]

    def __str__(self):
        return f"{self._field_name} {self.__class__.operator} %s"


class EqFilter(Filter):
    operator = '='


class NeqFilter(Filter):
    operator = '<>'


class GeFilter(Filter):
    operator = '>='


class GtFilter(Filter):
    operator = '>'


class LeFilter(Filter):
    operator = '<='


class LtFilter(Filter):
    operator = '<'


class LikeFilter(Filter):
    operator = 'LIKE'


class InFilter:
    """ IN """

    def __init__(self, field_name, values_range):
        self._field_name = field_name
        self._not = False

        if type(values_range) is SelectQuery:
            self._params = [p for p in values_range._params]
            self._subquery = values_range
        else:
            values_range = tuple(values_range)
            self._params = [values_range]
            self._subquery = None

    def __str__(self):
        operator = 'IN'
        if self._not == True:
            operator = 'NOT IN'

        if self._subquery is not None:
            return f'{self._field_name} {operator} ({str(self._subquery)})'
        else:
            return f'{self._field_name} {operator} %s'

    def __neg__(self):
        self._not = not self._not
        return self


class Field:
    """
    Поле.
    Используется для фильтров в запросах.
    """

    def __init__(self, name, table):
        self._name = name
        self._table = table
        self._name_verbose = f'{table._name}.{name}'

    @property
    def table(self):
        return self._table

    def __eq__(self, value):
        return EqFilter(self._name_verbose, value)

    def __ge__(self, value):
        return GeFilter(self._name_verbose, value)

    def __gt__(self, value):
        return GtFilter(self._name_verbose, value)

    def __le__(self, value):
        return LeFilter(self._name_verbose, value)

    def __lt__(self, value):
        return LtFilter(self._name_verbose, value)

    def __ne__(self, value):
        return NeqFilter(self._name_verbose, value)

    def __mod__(self, value):
        return LikeFilter(self._name_verbose, value)

    def __rshift__(self, value):
        return InFilter(self._name_verbose, value)


class Column:
    """
    Столбец.
    Используется для объединений.
    """

    def __init__(self, name, table):
        self._name = name
        self._table = table
        self._name_verbose = f'{table._name}.{name}'

    def _get_join(self, value, join_type):
        if type(value) is Column:
            field = value
            on = (self._name, field._name)

            if join_type == 'inner':
                j = Join
            elif join_type == 'left':
                j = LeftJoin
            elif join_type == 'right':
                j = RightJoin

            return j(self._table, field._table, on)
        else:
            raise TypeError(f'Недопустимый операнд: {value}')

    def __eq__(self, value):
        return self._get_join(value, 'inner')    

    def __lshift__(self, value):
        return self._get_join(value, 'left')

    def __rshift__(self, value):
        return self._get_join(value, 'right')


class ColumnSet:
    """
    Набор столбцов.
    """

    def __init__(self, columns):
        for col in columns:
            setattr(self, col._name, col)


class FieldSet:
    """
    Набор полей.
    """

    def __init__(self, fields):
        for field in fields:
            setattr(self, field._name, field)


class Table:
    """
    Таблица.
    """

    def __init__(self, name, fields):
        self._name = name
        self._fields_names = fields

        _columns, _fields = [], []
        for field in fields:
            _fields.append(Field(field, self))
            _columns.append(Column(field, self))
            
        self.fields = FieldSet(_fields)
        self.columns = ColumnSet(_columns)

    def has_field(self, field):
        return field in self._fields_names

    def get_fields_names(self):
        return self._fields_names

    def get_verbose_names(self):
        verbose_names = [f'{self._name}.{field}' for field in self._fields_names]
        return verbose_names

    def select(self, *fields):
        return SelectQuery(self, *fields)
