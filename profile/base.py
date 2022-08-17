from reports.func import Interpreter


class ReportProfile:
    """
    Профиль отчёта.
    """
    def __init__(self, **kwargs):
        self._sources = kwargs.get('sources', [])
        self._queries = kwargs.get('queries', [])
        self._schema = kwargs.get('schema', None)

    def _get_interpreter(self):
        return Interpreter()


class ReportComponent:
    """
    Компонент отчёта.
    """
    pass

    