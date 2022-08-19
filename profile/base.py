from noofa.func import Interpreter


class ProfileSchema:
    """
    Схема для отчёта.
    """
    def __init__(self, schema_dict={}):
        pass


class ReportProfile:
    """
    Профиль отчёта.
    """
    def __init__(self, schema, **kwargs):
        self._sources = kwargs.get('sources', {})  # источники данных
        self._queries = kwargs.get('queries', [])  # запросы
        self._dataframes = kwargs.get('dataframes', {})
        self._schema = kwargs.get('schema', None)

    def _get_interpreter(self):
        return Interpreter()


class ReportSchema:
    """
    Схема для компонента.
    """
    def __init__(self, schema_dict={}):
        pass


class ReportComponent:
    """
    Компонент отчёта.
    """
    def __init__(self, schema):
        self.name = schema.name
        self.sources = schema.sources


class ReportTable(ReportComponent):
    """
    Таблица в отчёте.
    """
    pass


class ReportChart(ReportComponent):
    """
    График в отчёте.
    """
    pass

    