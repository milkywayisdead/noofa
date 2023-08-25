class NoSuchFieldError(Exception):
    def __init__(self, field):
        self._field = field

    def __str__(self):
        return f'Поле {self._field} недоступно в запросе'


class TableHasNoFields(Exception):
    def __init__(self, table):
        self._table = table

    def __str__(self):
        return f'Таблица {self._table} не содержит полей либо не существует'
