
class ReportProfile:
    """
    Профиль отчёта.
    """
    def __init__(self, **kwargs):
        self._sources = kwargs.get('sources', [])
        self._queries = kwargs.get('queries', [])
        self._schema = kwargs.get('schema', None)


    