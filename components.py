class ComponentsSchema:
    """
    Схема компонентов отчёта.
    """
    def __init__(self, **kwargs):
        self._tables = kwargs.get('tables', {})
        self._charts = kwargs.get('charts', {})

    def from_json(self, json_schema):
        pass


class ReportTable:
    """
    Таблица в компонентах отчёта.
    """
    def __init__(self, dataframe, **options):
        pass

    def build(self):
        pass

    def to_csv(self):
        pass

    def to_xlsx(self):
        pass


class ReportChart:
    pass