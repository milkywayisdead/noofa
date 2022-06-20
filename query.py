from collections import namedtuple


class NoSuchFieldError(Exception):
    pass


class Join:
    join_type = 'INNER'

    def __init__(self, table1, table2, on):
        self._left = table1
        self._right = table2
        self._on = on

    def __str__(self):
        right_name, left_name = self._right._name, self._left._name
        s = f'{self.__class__.join_type} JOIN {right_name} '
        s += f'ON {left_name}.{self._on[0]} = {right_name}.{self._on[1]}'
        return s


class LeftJoin(Join):
    join_type = 'LEFT OUTER'


class SelectQuery:
    def __init__(self, table):
        self._fields = []
        self._where = []
        self._joins = []
        self._params = []
        self._table = table

    def join(self, *joins):
        for j in joins:
            self._joins.append(j)

        return self

    def where(self, *filters):
        for f in filters:
            self._where.append(f)
            for p in f._params:
                self._params.append(p)

        return self

    @property
    def params(self):
        return self._params

    def __str__(self):
        if self._fields:
            fields = f', '.join(self._fields)
        else:
            fields = '*'

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


class CompositeFilter:
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
        return self._params
    
    def __str__(self):
        filters = [str(f) for f in self._filters]
        s = f"({' AND '.join(filters)})"

        if self._q:
            for f in self._q:
                s += f" {f[1]} {str(f[0])}"

        return s

    def __and__(self, value):
        if type(value) is CompositeFilter:
            self._q.append((value, 'AND'))
            self._params += value._params
            return self

    def __or__(self, value):
        if type(value) is CompositeFilter:
            self._q.append((value, 'OR'))
            self._params += value._params
            return self


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


class Column:
    """
    Столбец.
    Используется для объединений.
    """

    def __init__(self, name, table):
        self._name = name
        self._table = table
        self._name_verbose = f'{table._name}.{name}'

    def __eq__(self, value):
        if type(value) is Column:
            field = value
            on = (self._name, field._name)
            j = Join(self._table, field._table, on)
            return j


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
        if field in self._fields_names:
            return True
        raise NoSuchFieldError

    def get_fields_names(self):
        return self._fields_names

    def get_verbose_names(self):
        verbose_names = [f'{self._name}.{field}' for field in self._fields_names]
        return verbose_names

    def select(self):
        return SelectQuery(table=self)
