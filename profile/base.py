

class ReportSchema:
    """
    Схема профиля отчётов.
    """
    def __init__(self, **kwargs):
        pass


class ReportProfile:
    """
    Профиль отчёта.
    """
    def __init__(self, **kwargs):
        self._sources = kwargs.get('sources', [])
        self._schema = kwargs.get('schema', None)


    def to_dict(self):
        pass

    