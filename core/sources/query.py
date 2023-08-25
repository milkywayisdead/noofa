from .exceptions import NoSuchFieldError, TableHasNoFields


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
        left_on, right_on = self._on[0], self._on[1]
        if self._left.enquote or self._right.enquote:
            right_name, left_name = f'"{right_name}"', f'"{left_name}"'
            left_on, right_on = f'"{left_on}"', f'"{right_on}"'
        s = f'{self.__class__.join_type} JOIN {right_name} '
        s += f'ON {left_name}.{left_on} = {right_name}.{right_on}'
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
        self._values = []  # список запрашиваемых полей
        self._order_by = []
        self._limit = None
        self._is_mssql = False

        for f in table.get_verbose_names():
            self._fields.append(f)

        self.values(*fields)

    @property
    def requested(self):
        if self._values:
            values = [v[0] if v[1] is None else v[1] for v in self._values]
            return values
        return self._fields

    def join(self, *joins):
        """
        Добавление объединения/объединений в запрос.
        """
        for j in joins:
            right, left = j._right, j._left
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
            if type(f) is Q:
                if not f.is_empty:
                    self._where.append(f)
            else:
                self._where.append(Q(f))
            for p in f._params:
                self._params.append(p)

        return self

    @property
    def params(self):
        """
        Список параметров в фильтрах запроса.
        """
        return self._params

    def values(self, *values):
        for value in values:
            f = value[0]
            if f in self._fields:
                if f not in self._values:
                    self._values.append(value)
            else:
                raise NoSuchFieldError(f)
        return self

    def limit(self, n):
        try:
            n = int(n)
        except:
            pass
        else:
            self._limit = n
        return self

    def mssql_limit(self, n):
        self._is_mssql = True
        return self.limit(n)

    def order_by(self, *ords):
        for o in ords:
            fields, sorting = o[0], o[1].upper()
            for field in fields:
                if field in self._fields:
                    pass
                else:
                    raise NoSuchFieldError(field)
            assert sorting in ['ASC', 'DESC'], 'Значение должно быть равно ASC либо DESC'
            ordby = f'{", ".join(fields)} {sorting}'
            if ordby not in self._order_by:
                self._order_by.append(ordby)
        return self

    def _execute(self, cursor):
        q = str(self)
        params = self._params

        if params:
            cursor.execute(q, params)
        else:
            cursor.execute(q)

        return cursor.fetchall()

    def str_and_params(self):
        return (str(self), self._params)

    def __str__(self):
        if self._values:
            values = [v[0] for v in self._values]
            fields = f', '.join(values)
        else:
            fields = f', '.join(self._fields)

        has_limit = self._limit is not None

        q_beg = f'SELECT TOP {self._limit}' if has_limit and self._is_mssql else 'SELECT'
        q = f'{q_beg} {fields} FROM {self._table._name}'

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

        if self._order_by:
            ordby = f' ORDER BY {", ".join(self._order_by)}'
            q += ordby

        if has_limit and not self._is_mssql:
            q += f' LIMIT {self._limit}'

        return q.rstrip()


class Q:
    """
    Составной фильтр.
    """
    def __init__(self, *filters):
        self._filters = ['AND', ]
        self._params = []

        for f in filters:
            self._filters.append(f)
            for p in f._params:
                self._params.append(p)

    @property
    def is_empty(self):
        """
        Является фильтр пустым, т.е. не содержащим дургие фильтры.
        """
        return len(self._filters) < 2

    @property
    def params(self):
        """
        Список параметров в фильтрах запроса.
        """
        return self._params

    def _to_str(self, filters):
        op = f' {filters[0]} '
        res = []
        for i in filters[1:]:
            if type(i) is str:
                continue
            if type(i) is list:
                i = self._to_str(i)
                if i:
                    res.append(i)
            else:
                i = str(i)
                if i:
                    res.append(i)

        s = f'{op.join(res)}'
        if len(res) > 1:
            s = f'({s})'

        return s

    def __str__(self):
        return self._to_str(self._filters)

    def _add_q(self, value, disj=False):
        if type(value) is Q:
            if value.is_empty:
                return self
            if self.is_empty:
                return value

            q = Q()
            if disj:
                q._filters = ['OR', ]
            else:
                q._filters = ['AND', ]

            q._filters.append(self._filters)
            q._filters.append(value._filters)
            q._params += self._params
            q._params += value._params
            return q
        raise TypeError(f'Недопустимый операнд: {value}')

    def __and__(self, value):
        """
        Логическое умножение (AND) с другими составными фильтрами.
        """
        return self._add_q(value)

    def __or__(self, value):
        """
        Логическое сложение (OR) с другими составными фильтрами.
        """
        return self._add_q(value, disj=True)


class Filter:
    """
    Фильтр (WHERE в запросе).
    """

    def __init__(self, field_name, value, param_placeholder='%s'):
        self._field_name = field_name
        self._params = [value]
        self._param_placeholder = param_placeholder

    def __str__(self):
        return f"{self._field_name} {self.__class__.operator} {self._param_placeholder}"


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


class ContainsFilter(Filter):
    operator = 'LIKE'

    def __init__(self, field_name, value, param_placeholder='%s'):
        self._field_name = field_name
        self._params = [f'%{value}%']
        self._param_placeholder = param_placeholder


class StartsWithFilter(Filter):
    operator = 'LIKE'

    def __init__(self, field_name, value, param_placeholder='%s'):
        self._field_name = field_name
        self._params = [f'{value}%']
        self._param_placeholder = param_placeholder


class EndsWithFilter(Filter):
    operator = 'LIKE'

    def __init__(self, field_name, value, param_placeholder='%s'):
        self._field_name = field_name
        self._params = [f'%{value}']
        self._param_placeholder = param_placeholder


class InFilter:
    """ IN """

    _not = False

    def __init__(self, field_name, values_range, param_placeholder='%s'):
        self._field_name = field_name
        self._not = False
        self._param_placeholder = param_placeholder

        if type(values_range) is SelectQuery:
            self._params = [p for p in values_range._params]
            self._subquery = values_range
        else:
            self._params = values_range
            self._subquery = None

    def __str__(self):
        operator = 'IN'
        if self.__class__._not == True:
            operator = 'NOT IN'

        if self._subquery is not None:
            return f'{self._field_name} {operator} ({str(self._subquery)})'
        else:
            placeholder = self._param_placeholder
            if self._params:
                if placeholder == '?':
                    params_list = ', '.join(placeholder*len(self._params))
                    return f'{self._field_name} {operator} ({params_list})'
                else:
                    params_list = ', '.join([placeholder]*len(self._params))
                return f'{self._field_name} {operator} ({placeholder})' % params_list
            else:
                return '1 = 1' if self._not else '1 = 2'

    def __neg__(self):
        self._not = not self._not
        return self


class NotInFilter(InFilter):
    _not = True


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
        return ContainsFilter(self._name_verbose, value)

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

    def __getitem__(self, key):
        return getattr(self, key)


class FieldSet:
    """
    Набор полей.
    """

    def __init__(self, fields):
        self._empty = len(fields) == 0
        for field in fields:
            setattr(self, field._name, field)

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def is_empty(self):
        return self._empty


class Table:
    """
    Таблица.
    """

    def __init__(self, name, fields, enquote=False):
        self._name = name
        self._fields_names = fields
        self.enquote = enquote  # брать ли в кавычки названия таблицы и полей

        _columns, _fields = [], []
        for field in fields:
            _fields.append(Field(field, self))
            _columns.append(Column(field, self))

        self.fields = FieldSet(_fields)
        self.columns = ColumnSet(_columns)
        if self.fields.is_empty:
            raise TableHasNoFields(self._name)

    @property
    def has_no_fields(self):
        return False

    def has_field(self, field):
        """
        Проверка, есть ли поле в таблице.
        """
        if field in self._fields_names:
            return True
        raise NoSuchFieldError(field)

    def get_fields_names(self):
        """
        Список полей таблицы.
        """
        return self._fields_names

    def get_verbose_names(self):
        """
        Список полных названий полей (с названием таблице в префиксе).
        """
        if self.enquote:
            verbose_names = [f'"{self._name}"."{field}"' for field in self._fields_names]
        else:    
            verbose_names = [f'{self._name}.{field}' for field in self._fields_names]
        return verbose_names

    def select(self, *fields):
        """
        Создание объекта простого select-запроса.
        """
        return SelectQuery(self, *fields)
