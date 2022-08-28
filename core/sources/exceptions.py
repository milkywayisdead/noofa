class NoSuchFieldError(Exception):
    def __init__(self, field):
        self._field = field

    def __str__(self):
        return f'Поле {self._field} недоступно в запросе'